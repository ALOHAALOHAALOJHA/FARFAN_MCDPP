import sys
from pathlib import Path
import asyncio

# Setup path
ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from src.dashboard_atroz_.ingestion import DashboardIngester

async def main():
    print("Verifying Dashboard Wiring...")
    ingester = DashboardIngester()

    # Mock Context
    class MockInputData:
        document_id = "DOC-19050"
        pdf_path = "data/19050_Argelia.pdf"

    class MockDoc:
        input_data = MockInputData()

    class MockMacro:
        macro_score = 85.5
        class Details:
            quality_band = "OPTIMAL"
        details = Details()

    class MockCluster:
        cluster_id = "CL01"
        score = 90.0

    context = {
        "document": MockDoc(),
        "macro_result": MockMacro(),
        "cluster_scores": [MockCluster()],
        "scored_results": []
    }

    success = await ingester.ingest_results(context)
    if success:
        print("✅ Wiring verification passed: Ingestion triggered successfully.")
    else:
        print("❌ Wiring verification failed.")

if __name__ == "__main__":
    asyncio.run(main())
