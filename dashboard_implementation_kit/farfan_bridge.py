"""
FARFAN Bridge
Connects the core pipeline artifacts to the Dashboard Database.
"""
import sys
import os
import json
import logging
from pathlib import Path
from typing import Any, Dict, Optional

# Configure path to import src
# Assuming this script is in /dashboard_implementation_kit/
ROOT_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT_DIR))

try:
    from src.dashboard_atroz_.dashboard_data_service import DashboardDataService
    from src.dashboard_atroz_.pdet_colombia_data import PDET_MUNICIPALITIES, PDETSubregion
except ImportError as e:
    print(f"Error importing FARFAN modules: {e}")
    sys.exit(1)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("farfan_bridge")

def get_db_connection():
    """
    Establish database connection.
    For the quickstart, we will return a mock or a sqlite connection if configured.
    """
    # TODO: Implement real PostgreSQL connection using psycopg2 or sqlalchemy
    # import psycopg2
    # return psycopg2.connect(os.environ.get("DATABASE_URL"))
    return None

def _generate_upsert_sql(table: str, data: Dict[str, Any], conflict_key: str) -> str:
    """Generates a PostgreSQL UPSERT statement."""
    columns = list(data.keys())
    values = []
    for col in columns:
        val = data[col]
        if val is None:
            values.append("NULL")
        elif isinstance(val, (str, Path)):
            safe_val = str(val).replace("'", "''")
            values.append(f"'{safe_val}'")
        else:
            values.append(str(val))

    cols_str = ", ".join(columns)
    vals_str = ", ".join(values)

    update_parts = [f"{col} = EXCLUDED.{col}" for col in columns if col != conflict_key]
    update_str = ", ".join(update_parts)

    return f"INSERT INTO {table} ({cols_str}) VALUES ({vals_str}) ON CONFLICT ({conflict_key}) DO UPDATE SET {update_str};"

def ingest_municipality(municipality: Any, data_service: DashboardDataService, db: Any):
    """
    Ingest a single municipality's data into the database.
    """
    logger.info(f"Ingesting {municipality.name} ({municipality.dane_code})...")

    # Simulate finding a job/report for this municipality
    # In a real run, we would look up the job_id for this municipality
    # For now, we construct a context from what we know

    mock_record = {
        "id": municipality.dane_code,
        "name": municipality.name,
        "municipality": municipality.name,
        "job_id": f"JOB-{municipality.dane_code}",
        "updated_at": "2024-05-20T10:00:00Z"
    }

    try:
        # data_service.summarize_region tries to load from disk.
        # If no file, it returns structure with Nones.
        summary, context = data_service.summarize_region(mock_record)

        # 1. Prepare Region Data
        region_data = {
            "dane_code": municipality.dane_code,
            "name": municipality.name,
            "department": municipality.department,
            "subregion_id": municipality.subregion.name if municipality.subregion else None,
            "population": municipality.population,
            "area_km2": municipality.area_km2,
            "latest_job_id": mock_record["job_id"],
            "macro_score": summary.get('scores', {}).get('overall'),
            "macro_band": summary.get('macroBand'),
        }

        sql = _generate_upsert_sql("regions", region_data, "dane_code")

        if db:
            # db.execute(sql)
            pass
        else:
            # Dry run: just log the first few chars
            logger.info(f"  [DRY RUN] Generated SQL for Region: {sql.strip()[:80]}...")

        # 2. Prepare Cluster Scores
        clusters = summary.get('clusterScores', {})
        for cluster_id, score in clusters.items():
            cluster_data = {
                "region_id": f"(SELECT id FROM regions WHERE dane_code='{municipality.dane_code}')", # Subquery for FK
                "cluster_id": cluster_id,
                "score_percent": score,
            }
            # Note: SQL generation for this would be slightly different due to the subquery value
            pass

    except Exception as e:
        logger.error(f"Failed to process {municipality.name}: {e}", exc_info=True)

def main():
    logger.info("Starting FARFAN Bridge...")

    jobs_dir = ROOT_DIR / "output" # Default output dir

    service = DashboardDataService(jobs_dir=jobs_dir)
    db = get_db_connection()

    if not db:
        logger.warning("No database connection. Running in DRY RUN mode (generating SQL logs).")

    count = 0
    limit = 3 # Reduced limit for cleaner log
    for municipality in PDET_MUNICIPALITIES:
        ingest_municipality(municipality, service, db)
        count += 1
        if count >= limit:
            break

    logger.info(f"Bridge test complete. Processed {count} municipalities.")

if __name__ == "__main__":
    main()
