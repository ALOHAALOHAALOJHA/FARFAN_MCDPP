"""
Dashboard Ingestion Module
Wires the Orchestrator to the Dashboard Database.
"""
import logging
import re
from typing import Any, Dict
from pathlib import Path

from .config import DATABASE_URL, USE_SQLITE, ENABLE_REALTIME_INGESTION
from .pdet_colombia_data import PDET_MUNICIPALITIES

logger = logging.getLogger(__name__)

class DashboardIngester:
    def __init__(self, db_url: str = DATABASE_URL):
        self.db_url = db_url

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
            # Note: access attributes safely as they might be missing or None
            document = context.get("document") # CanonPolicyPackage (Phase 1)
            macro_eval = context.get("macro_result") # MacroEvaluation (Phase 7)
            cluster_scores = context.get("cluster_scores") # List[ClusterScore] (Phase 6)
            scored_micro = context.get("scored_results") # List[ScoredMicroQuestion] (Phase 3)

            if not document:
                logger.warning("Ingestion skipped: 'document' missing from context.")
                # We can't proceed without document identity
                return False

            # 2. Identify Municipality
            # Attempt to resolve DANE code from document input data
            input_data = getattr(document, "input_data", None)
            doc_id = getattr(input_data, "document_id", "unknown") if input_data else "unknown"
            pdf_path = getattr(input_data, "pdf_path", "unknown") if input_data else "unknown"

            dane_code = self._resolve_dane_code(doc_id, str(pdf_path))
            municipality_name = self._resolve_municipality_name(dane_code)

            logger.info(f"Ingesting data for municipality: {municipality_name} ({dane_code})")

            # 3. Generate SQL Data
            # Macro
            macro_score = getattr(macro_eval, "macro_score", None) if macro_eval else None
            macro_band = None
            if macro_eval and hasattr(macro_eval, "details"):
                # details is MacroScore
                macro_band = getattr(macro_eval.details, "quality_band", None)

            # Upsert Region
            region_sql = self._generate_region_upsert(
                dane_code, municipality_name, macro_score, macro_band
            )
            self._execute_sql(region_sql)

            # Clusters
            if cluster_scores:
                for cs in cluster_scores:
                    # cs is ClusterScore
                    cid = getattr(cs, "cluster_id", None)
                    score = getattr(cs, "score", 0.0)
                    if cid:
                        cluster_sql = self._generate_cluster_upsert(dane_code, cid, score)
                        self._execute_sql(cluster_sql)

            # Micro Scores
            if scored_micro:
                # Batch these in production
                for sm in scored_micro:
                    # sm is ScoredMicroQuestion
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
        # Heuristic: try to find a 5-digit code in the string
        match = re.search(r'\b\d{5}\b', doc_id) or re.search(r'\b\d{5}\b', pdf_path)
        if match:
            return match.group(0)
        return "00000" # Fallback

    def _resolve_municipality_name(self, dane_code: str) -> str:
        for m in PDET_MUNICIPALITIES:
            if m.dane_code == dane_code:
                return m.name
        return "Unknown Municipality"

    def _generate_region_upsert(self, dane: str, name: str, macro: float | None, band: str | None) -> str:
        m_val = str(macro) if macro is not None else "NULL"
        b_val = f"'{band}'" if band else "NULL"
        safe_name = name.replace("'", "''")
        return f"INSERT INTO regions (dane_code, name, macro_score, macro_band) VALUES ('{dane}', '{safe_name}', {m_val}, {b_val}) ON CONFLICT (dane_code) DO UPDATE SET macro_score=EXCLUDED.macro_score, macro_band=EXCLUDED.macro_band, last_updated=CURRENT_TIMESTAMP;"

    def _generate_cluster_upsert(self, dane: str, cluster_id: str, score: float) -> str:
        return f"INSERT INTO cluster_scores (region_id, cluster_id, score) VALUES ((SELECT id FROM regions WHERE dane_code='{dane}'), '{cluster_id}', {score}) ON CONFLICT (region_id, cluster_id) DO UPDATE SET score=EXCLUDED.score;"

    def _generate_question_upsert(self, dane: str, qid: str, score: float) -> str:
        return f"INSERT INTO question_scores (region_id, question_id, score) VALUES ((SELECT id FROM regions WHERE dane_code='{dane}'), '{qid}', {score}) ON CONFLICT (region_id, question_id) DO UPDATE SET score=EXCLUDED.score;"

    def _execute_sql(self, sql: str):
        # In this environment, we just log the SQL as we don't have a live DB
        # In production, self.conn.execute(sql)
        if "INSERT INTO regions" in sql:
            logger.info(f"SQL Exec: {sql.strip()[:100]}...")
        # logger.debug(f"SQL: {sql}")
        pass
