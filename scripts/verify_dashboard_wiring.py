import sys
from pathlib import Path
import asyncio

# Setup path
ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from src.dashboard_atroz_.ingestion import DashboardIngester

async def main():
    print("Verifying Dashboard Wiring and Data Availability...")
    ingester = DashboardIngester()

    # 1. Populate Ref Data
    try:
        ingester.populate_reference_data()
        print("✅ Reference data population triggered (Simulated DB).")
    except Exception as e:
        print(f"❌ Reference data population failed: {e}")

    # 2. Test Ingestion with Fuzzy Name Matching
    print("\nTesting Matching Logic:")

    # Mock Context with filename-based identification
    class MockInputData:
        document_id = "DOC-UNKNOWN-ID"
        # "Argelia" should match Argelia (Cauca) 19050
        pdf_path = "data/Plan_De_Desarrollo_Argelia_Cauca_2024.pdf"

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
        print("✅ Fuzzy matching & Ingestion successful.")
    else:
        print("❌ Fuzzy matching failed.")

if __name__ == "__main__":
    asyncio.run(main())
