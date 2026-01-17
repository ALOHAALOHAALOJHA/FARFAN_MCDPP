import logging
import sys
from pathlib import Path

# Add src to path for standalone execution
_repo_root = Path(__file__).resolve().parent
_src_path = _repo_root / "src"
if str(_src_path) not in sys.path:
    sys.path.insert(0, str(_src_path))

from farfan_pipeline.infrastructure.extractors.financial_chain_extractor import FinancialChainExtractor
from farfan_pipeline.infrastructure.extractors.causal_verb_extractor import CausalVerbExtractor
from farfan_pipeline.infrastructure.extractors.institutional_ner_extractor import InstitutionalNERExtractor

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def main():
    print("=== Verifying Critical Extractors ===")
    
    extractors = [
        FinancialChainExtractor(),
        CausalVerbExtractor(),
        InstitutionalNERExtractor()
    ]
    
    for extractor in extractors:
        print(f"\nTesting {extractor.__class__.__name__}...")
        try:
            results = extractor.self_test()
            print(f"Pass Rate: {results['pass_rate']:.2%}")
            if results['failed'] > 0:
                print(f"Failures: {results['failed']}")
                for fail in results['failures']:
                    print(f" - {fail}")
        except Exception as e:
            print(f"Error running self-test: {e}")

if __name__ == "__main__":
    main()

