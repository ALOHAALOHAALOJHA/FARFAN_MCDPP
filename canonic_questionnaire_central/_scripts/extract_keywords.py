#!/usr/bin/env python3
"""
Script para extraer y consolidar keywords para CQC v2.0.

Extrae keywords de:
1. policy_areas/PA*/keywords.json
2. clusters/CL*/metadata.json (si contienen keywords)

Genera:
- _registry/keywords/index.json (índice maestro)
- _registry/keywords/by_policy_area/*.json
- _registry/keywords/by_cluster/*.json

Autor: CQC Migration System
Versión: 2.0.0
Fecha: 2026-01-06
"""

import json
import logging
from pathlib import Path
from datetime import datetime, timezone
from typing import Dict, List, Any, Set
from collections import defaultdict

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

CQC_ROOT = Path(__file__).parent.parent
POLICY_AREAS = CQC_ROOT / "policy_areas"
CLUSTERS = CQC_ROOT / "clusters"
OUTPUT_DIR = CQC_ROOT / "_registry" / "keywords"


class KeywordExtractor:
    """Extractor y consolidador de keywords."""

    def __init__(self):
        self.keywords_by_pa: Dict[str, List[str]] = {}
        self.keywords_by_cluster: Dict[str, List[str]] = {}
        self.all_keywords: Set[str] = set()
        self.keyword_to_pas: Dict[str, List[str]] = defaultdict(list)

    def extract_from_policy_areas(self) -> None:
        """Extrae keywords de policy_areas."""
        logger.info(f"Extracting keywords from {POLICY_AREAS}...")

        if not POLICY_AREAS.exists():
            logger.warning(f"{POLICY_AREAS} not found")
            return

        for pa_dir in sorted(POLICY_AREAS.iterdir()):
            if not pa_dir.is_dir():
                continue

            pa_id = pa_dir.name
            keywords_file = pa_dir / "keywords.json"

            if not keywords_file.exists():
                logger.debug(f"  No keywords.json in {pa_id}")
                continue

            try:
                with open(keywords_file) as f:
                    data = json.load(f)
                    keywords = data.get("keywords", []) if isinstance(data, dict) else data

                    self.keywords_by_pa[pa_id] = keywords
                    self.all_keywords.update(keywords)

                    # Build reverse index
                    for kw in keywords:
                        self.keyword_to_pas[kw].append(pa_id)

                    logger.info(f"  ✓ {pa_id}: {len(keywords)} keywords")

            except Exception as e:
                logger.error(f"  Error loading {keywords_file}: {e}")

        logger.info(f"  Total from policy areas: {len(self.all_keywords)} unique keywords")

    def extract_from_clusters(self) -> None:
        """Extrae keywords de clusters (si existen)."""
        logger.info(f"Extracting keywords from {CLUSTERS}...")

        if not CLUSTERS.exists():
            logger.warning(f"{CLUSTERS} not found")
            return

        for cluster_dir in sorted(CLUSTERS.iterdir()):
            if not cluster_dir.is_dir():
                continue

            cluster_id = cluster_dir.name
            metadata_file = cluster_dir / "metadata.json"

            if not metadata_file.exists():
                continue

            try:
                with open(metadata_file) as f:
                    data = json.load(f)
                    keywords = data.get("keywords", [])

                    if keywords:
                        self.keywords_by_cluster[cluster_id] = keywords
                        self.all_keywords.update(keywords)
                        logger.info(f"  ✓ {cluster_id}: {len(keywords)} keywords")

            except Exception as e:
                logger.error(f"  Error loading {metadata_file}: {e}")

        logger.info(f"  Total from clusters: {len(self.keywords_by_cluster)} clusters")

    def generate_index(self) -> Dict[str, Any]:
        """Genera índice maestro."""
        # Keyword reverse map
        keyword_map = {}
        for kw in sorted(self.all_keywords):
            keyword_map[kw] = {
                "keyword": kw,
                "policy_areas": self.keyword_to_pas.get(kw, []),
                "frequency": len(self.keyword_to_pas.get(kw, []))
            }

        return {
            "$schema": "https://json-schema.org/draft/2020-12/schema",
            "$id": "keywords-index-v2.0.0",
            "_meta": {
                "schema_version": "2.0.0",
                "generated_at": datetime.now(timezone.utc).isoformat(),
                "generator": "extract_keywords.py"
            },
            "statistics": {
                "total_unique_keywords": len(self.all_keywords),
                "total_policy_areas": len(self.keywords_by_pa),
                "total_clusters": len(self.keywords_by_cluster),
                "avg_keywords_per_pa": round(
                    sum(len(kws) for kws in self.keywords_by_pa.values()) / len(self.keywords_by_pa), 2
                ) if self.keywords_by_pa else 0
            },
            "keywords": keyword_map
        }

    def save_index(self, index: Dict[str, Any]) -> None:
        """Guarda índice maestro."""
        output_file = OUTPUT_DIR / "index.json"
        logger.info(f"Saving index to {output_file}...")

        OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(index, f, indent=2, ensure_ascii=False)

        logger.info(f"  ✓ Saved {len(index['keywords'])} keywords to index.json")

    def save_by_policy_area(self) -> None:
        """Guarda keywords por policy area."""
        output_dir = OUTPUT_DIR / "by_policy_area"
        logger.info(f"Saving keywords by policy area to {output_dir}...")

        output_dir.mkdir(parents=True, exist_ok=True)
        for pa_id, keywords in self.keywords_by_pa.items():
            output_file = output_dir / f"{pa_id}.json"

            with open(output_file, "w", encoding="utf-8") as f:
                json.dump({
                    "policy_area_id": pa_id,
                    "keyword_count": len(keywords),
                    "keywords": sorted(keywords)
                }, f, indent=2, ensure_ascii=False)

            logger.debug(f"  ✓ Saved {pa_id}.json")

        logger.info(f"  ✓ Saved {len(self.keywords_by_pa)} policy area files")

    def save_by_cluster(self) -> None:
        """Guarda keywords por cluster."""
        if not self.keywords_by_cluster:
            logger.info("  No cluster keywords to save")
            return

        output_dir = OUTPUT_DIR / "by_cluster"
        logger.info(f"Saving keywords by cluster to {output_dir}...")

        output_dir.mkdir(parents=True, exist_ok=True)
        for cluster_id, keywords in self.keywords_by_cluster.items():
            output_file = output_dir / f"{cluster_id}.json"

            with open(output_file, "w", encoding="utf-8") as f:
                json.dump({
                    "cluster_id": cluster_id,
                    "keyword_count": len(keywords),
                    "keywords": sorted(keywords)
                }, f, indent=2, ensure_ascii=False)

        logger.info(f"  ✓ Saved {len(self.keywords_by_cluster)} cluster files")

    def generate_schema(self) -> None:
        """Genera JSON schema."""
        schema = {
            "$schema": "https://json-schema.org/draft/2020-12/schema",
            "$id": "keyword-schema-v2.0.0",
            "title": "CQC Keyword Schema",
            "description": "Schema para keywords en CQC v2.0",
            "type": "object",
            "oneOf": [
                {"required": ["policy_area_id", "keywords"]},
                {"required": ["cluster_id", "keywords"]}
            ],
            "properties": {
                "policy_area_id": {"type": "string", "pattern": "^PA\\d{2}"},
                "cluster_id": {"type": "string", "pattern": "^CL\\d{2}"},
                "keyword_count": {"type": "integer", "minimum": 0},
                "keywords": {
                    "type": "array",
                    "items": {"type": "string"},
                    "uniqueItems": True
                }
            }
        }

        output_file = OUTPUT_DIR / "schema.json"
        OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(schema, f, indent=2)

        logger.info("  ✓ Generated schema.json")

    def extract(self) -> bool:
        """Ejecuta extracción completa."""
        logger.info("🔄 Starting keyword extraction...")

        try:
            self.extract_from_policy_areas()
            self.extract_from_clusters()

            index = self.generate_index()
            self.save_index(index)
            self.save_by_policy_area()
            self.save_by_cluster()
            self.generate_schema()

            logger.info("\n" + "="*80)
            logger.info("✅ KEYWORD EXTRACTION COMPLETED")
            logger.info("="*80)
            logger.info(f"  Total unique keywords: {len(self.all_keywords)}")
            logger.info(f"  Policy areas processed: {len(self.keywords_by_pa)}")
            logger.info(f"  Clusters processed: {len(self.keywords_by_cluster)}")
            logger.info(f"  Output location: {OUTPUT_DIR}")
            logger.info("="*80)

            return True

        except Exception as e:
            logger.error(f"❌ Extraction failed: {e}")
            import traceback
            traceback.print_exc()
            return False


def main():
    import argparse
    parser = argparse.ArgumentParser(description="Extract keywords to CQC v2.0")
    parser.add_argument("--verbose", "-v", action="store_true", help="Verbose output")

    args = parser.parse_args()

    if args.verbose:
        logger.setLevel(logging.DEBUG)

    extractor = KeywordExtractor()
    success = extractor.extract()

    return 0 if success else 1


if __name__ == "__main__":
    import sys
    sys.exit(main())
