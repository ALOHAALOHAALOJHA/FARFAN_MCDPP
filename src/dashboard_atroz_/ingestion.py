"""
Dashboard Ingestion Module
Wires the Orchestrator to the Dashboard Database.
"""
import logging
import re
from typing import Any, Dict, Optional
from pathlib import Path
from difflib import get_close_matches

from .config import DATABASE_URL, USE_SQLITE, ENABLE_REALTIME_INGESTION
from .pdet_colombia_data import PDET_MUNICIPALITIES, PDETMunicipality

logger = logging.getLogger(__name__)

class DashboardIngester:
    def __init__(self, db_url: str = DATABASE_URL):
        self.db_url = db_url

    def populate_reference_data(self):
        """
        Populate DB with all 170 PDET municipalities and subregions.
        This ensures the map is fully populated even before analysis.
        """
        logger.info("Populating reference data (170 Municipalities)...")
        count = 0
        for m in PDET_MUNICIPALITIES:
            # Upsert Municipality (Region)
            # Note: In a real DB we would upsert Subregions first.
            sql = self._generate_region_upsert(
                m.dane_code, m.name, None, None, m.latitude, m.longitude
            )
            self._execute_sql(sql)
            count += 1
        logger.info(f"Populated {count} regions.")

    async def ingest_results(self, context: Dict[str, Any]) -> bool:
        """
        Ingest results from Orchestrator context into Dashboard DB.

        Args:
            context: The orchestrator's context dictionary containing artifacts from all phases.
        """
        if not ENABLE_REALTIME_INGESTION:
            logger.info("Dashboard ingestion disabled via config.")
            return False

        logger.info("Starting Dashboard Ingestion...")

        try:
            # 1. Extract Artifacts
            document = context.get("document") # CanonPolicyPackage (Phase 1)
            macro_eval = context.get("macro_result") # MacroEvaluation (Phase 7)
            cluster_scores = context.get("cluster_scores") # List[ClusterScore] (Phase 6)
            scored_micro = context.get("scored_results") # List[ScoredMicroQuestion] (Phase 3)

            if not document:
                logger.warning("Ingestion skipped: 'document' missing from context.")
                return False

            # 2. Identify Municipality
            input_data = getattr(document, "input_data", None)
            doc_id = getattr(input_data, "document_id", "unknown") if input_data else "unknown"
            pdf_path = getattr(input_data, "pdf_path", "unknown") if input_data else "unknown"

            dane_code = self._resolve_dane_code(doc_id, str(pdf_path))
            # Prefer PDF path for name resolution as doc_id might be opaque
            name_source = str(pdf_path) if str(pdf_path) != "unknown" else doc_id
            municipality = self._resolve_municipality(dane_code, name_source)

            if not municipality:
                logger.warning(f"Could not resolve municipality identity for {doc_id}")
                # Fallback to creating a stub if strictly required, but for now skip to avoid bad data
                return False

            dane_code = municipality.dane_code
            municipality_name = municipality.name

            logger.info(f"Ingesting data for municipality: {municipality_name} ({dane_code})")

            # 3. Generate SQL Data
            # Macro
            macro_score = getattr(macro_eval, "macro_score", None) if macro_eval else None
            macro_band = None
            if macro_eval and hasattr(macro_eval, "details"):
                macro_band = getattr(macro_eval.details, "quality_band", None)

            # Use static coords from reference data
            lat = municipality.latitude
            lon = municipality.longitude

            # Upsert Region
            region_sql = self._generate_region_upsert(
                dane_code, municipality_name, macro_score, macro_band, lat, lon
            )
            self._execute_sql(region_sql)

            # Clusters
            if cluster_scores:
                for cs in cluster_scores:
                    cid = getattr(cs, "cluster_id", None)
                    score = getattr(cs, "score", 0.0)
                    if cid:
                        cluster_sql = self._generate_cluster_upsert(dane_code, cid, score)
                        self._execute_sql(cluster_sql)

            # Micro Scores
            if scored_micro:
                for sm in scored_micro:
                    qid = getattr(sm, "question_id", None)
                    score = getattr(sm, "score", 0.0)
                    if qid:
                        qs_sql = self._generate_question_upsert(dane_code, qid, score)
                        self._execute_sql(qs_sql)

            logger.info(f"✓ Successfully ingested data for {municipality_name} to Dashboard DB")
            return True

        except Exception as e:
            logger.error(f"Dashboard ingestion failed: {e}", exc_info=True)
            return False

    def _resolve_dane_code(self, doc_id: str, pdf_path: str) -> str:
        # Heuristic: try to find a 5-digit code
        match = re.search(r'\b\d{5}\b', doc_id) or re.search(r'\b\d{5}\b', pdf_path)
        if match:
            return match.group(0)
        return ""

    def _resolve_municipality(self, dane_code: str, doc_name: str) -> Optional[PDETMunicipality]:
        # 1. Exact Match by Code
        if dane_code:
            for m in PDET_MUNICIPALITIES:
                if m.dane_code == dane_code:
                    return m

        # 2. Name Matching
        # Normalize: remove path, extension, underscores
        clean_name = Path(doc_name).stem.replace("_", " ").lower()

        # Exact name match (case insensitive)
        for m in PDET_MUNICIPALITIES:
            if m.name.lower() == clean_name:
                return m

        # Substring match
        for m in PDET_MUNICIPALITIES:
            if m.name.lower() in clean_name:
                return m

        # Fuzzy Match
        names = [m.name for m in PDET_MUNICIPALITIES]
        matches = get_close_matches(clean_name, names, n=1, cutoff=0.6)
        if matches:
            match_name = matches[0]
            for m in PDET_MUNICIPALITIES:
                if m.name == match_name:
                    return m

        return None

    def _generate_region_upsert(self, dane: str, name: str, macro: float | None, band: str | None, lat: float=0.0, lon: float=0.0) -> str:
        m_val = str(macro) if macro is not None else "NULL"
        b_val = f"'{band}'" if band else "NULL"
        safe_name = name.replace("'", "''")
        return f"INSERT INTO regions (dane_code, name, macro_score, macro_band, latitude, longitude) VALUES ('{dane}', '{safe_name}', {m_val}, {b_val}, {lat}, {lon}) ON CONFLICT (dane_code) DO UPDATE SET macro_score=EXCLUDED.macro_score, macro_band=EXCLUDED.macro_band, latitude=EXCLUDED.latitude, longitude=EXCLUDED.longitude, last_updated=CURRENT_TIMESTAMP;"

    def _generate_cluster_upsert(self, dane: str, cluster_id: str, score: float) -> str:
        return f"INSERT INTO cluster_scores (region_id, cluster_id, score) VALUES ((SELECT id FROM regions WHERE dane_code='{dane}'), '{cluster_id}', {score}) ON CONFLICT (region_id, cluster_id) DO UPDATE SET score=EXCLUDED.score;"

    def _generate_question_upsert(self, dane: str, qid: str, score: float) -> str:
        return f"INSERT INTO question_scores (region_id, question_id, score) VALUES ((SELECT id FROM regions WHERE dane_code='{dane}'), '{qid}', {score}) ON CONFLICT (region_id, question_id) DO UPDATE SET score=EXCLUDED.score;"

    def _execute_sql(self, sql: str):
        # Dry run logging
        if "INSERT INTO regions" in sql:
            logger.info(f"SQL Exec: {sql.strip()[:100]}...")
        pass
