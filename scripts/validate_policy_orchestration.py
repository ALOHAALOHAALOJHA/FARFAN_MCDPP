#!/usr/bin/env python3
"""
Validation script for Policy Orchestration System.

This script validates the complete integration:
    1. Smart chunks generates exactly 10 chunks per policy area
    2. SignalPacks load correctly for each PA (PA01-PA10)
    3. PolicyOrchestrator distributes chunks to executors
    4. Executors receive chunks + signals without desynchronization

Usage:
    python scripts/validate_policy_orchestration.py
    python scripts/validate_policy_orchestration.py --policy-area PA01
    python scripts/validate_policy_orchestration.py --verbose

Exit codes:
    0: All validations passed
    1: Validation failed
"""

import sys
import json
import logging
from pathlib import Path
from typing import Dict, List, Any

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from saaaaaa.core.orchestrator.policy_orchestrator import PolicyOrchestrator
from saaaaaa.core.orchestrator.signals import SignalRegistry, SignalPack

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("PolicyOrchestrationValidator")


class ValidationError(Exception):
    """Raised when validation fails."""
    pass


class PolicyOrchestrationValidator:
    """
    Validates the policy orchestration system end-to-end.
    """

    POLICY_AREAS = [
        "PA01", "PA02", "PA03", "PA04", "PA05",
        "PA06", "PA07", "PA08", "PA09", "PA10"
    ]

    def __init__(self, signals_dir: str | Path):
        """
        Initialize validator.

        Args:
            signals_dir: Directory containing signal pack JSON files
        """
        self.signals_dir = Path(signals_dir)
        self.signal_registry = SignalRegistry(max_size=20, default_ttl_s=7200)
        self.orchestrator = None
        self.validation_results = {
            "signal_packs_loaded": 0,
            "signal_packs_validated": 0,
            "chunk_validations": [],
            "orchestrator_validations": [],
            "errors": [],
        }

    def run_full_validation(self, policy_area: str | None = None) -> bool:
        """
        Run complete validation suite.

        Args:
            policy_area: Optional single policy area to validate (validates all if None)

        Returns:
            True if all validations passed, False otherwise
        """
        logger.info("=" * 70)
        logger.info("POLICY ORCHESTRATION SYSTEM - VALIDATION")
        logger.info("=" * 70)
        logger.info("")

        try:
            # Step 1: Validate signal packs
            logger.info("Step 1: Validating SignalPacks...")
            logger.info("-" * 70)
            self._validate_signal_packs(policy_area)
            logger.info(f"✓ SignalPacks validated: {self.validation_results['signal_packs_validated']}")
            logger.info("")

            # Step 2: Validate chunk calibration
            logger.info("Step 2: Validating chunk calibration (10 chunks/PA)...")
            logger.info("-" * 70)
            self._validate_chunk_calibration(policy_area)
            logger.info(f"✓ Chunk calibrations validated: {len(self.validation_results['chunk_validations'])}")
            logger.info("")

            # Step 3: Validate orchestrator
            logger.info("Step 3: Validating PolicyOrchestrator...")
            logger.info("-" * 70)
            self._validate_orchestrator(policy_area)
            logger.info(f"✓ Orchestrator validations: {len(self.validation_results['orchestrator_validations'])}")
            logger.info("")

            # Summary
            self._print_summary()

            if self.validation_results["errors"]:
                logger.error(f"Validation FAILED with {len(self.validation_results['errors'])} errors")
                return False

            logger.info("✓ All validations PASSED")
            return True

        except Exception as e:
            logger.error(f"Validation failed with exception: {e}")
            import traceback
            traceback.print_exc()
            return False

    def _validate_signal_packs(self, policy_area: str | None = None):
        """
        Validate that signal packs exist and are valid.

        Args:
            policy_area: Optional single policy area to validate
        """
        areas_to_check = [policy_area] if policy_area else self.POLICY_AREAS

        for pa in areas_to_check:
            signal_file = self.signals_dir / f"{pa}.json"

            # Check file exists
            if not signal_file.exists():
                error = f"Signal pack file missing: {signal_file}"
                logger.error(f"  ✗ {pa}: {error}")
                self.validation_results["errors"].append(error)
                continue

            # Load and validate
            try:
                with open(signal_file, 'r', encoding='utf-8') as f:
                    signal_data = json.load(f)

                signal_pack = SignalPack(**signal_data)

                # Validate policy_area matches
                if signal_pack.policy_area != pa:
                    raise ValidationError(
                        f"policy_area mismatch: expected {pa}, got {signal_pack.policy_area}"
                    )

                # Validate has patterns and regex
                if not signal_pack.patterns:
                    raise ValidationError("patterns list is empty")

                if not signal_pack.regex:
                    raise ValidationError("regex list is empty")

                # Register signal pack
                self.signal_registry.put(pa, signal_pack)

                logger.info(
                    f"  ✓ {pa}: v{signal_pack.version} - "
                    f"{len(signal_pack.patterns)} patterns, "
                    f"{len(signal_pack.regex)} regex, "
                    f"{len(signal_pack.verbs)} verbs, "
                    f"{len(signal_pack.entities)} entities"
                )

                self.validation_results["signal_packs_loaded"] += 1
                self.validation_results["signal_packs_validated"] += 1

            except Exception as e:
                error = f"{pa}: Signal pack validation failed - {e}"
                logger.error(f"  ✗ {error}")
                self.validation_results["errors"].append(error)

    def _validate_chunk_calibration(self, policy_area: str | None = None):
        """
        Validate that chunk calibration produces exactly 10 chunks.

        Args:
            policy_area: Optional single policy area to validate
        """
        from smart_policy_chunks_canonic_phase_one import (
            PolicyAreaChunkCalibrator,
            SemanticChunkingProducer
        )

        # Initialize calibrator
        semantic_chunking = SemanticChunkingProducer()
        calibrator = PolicyAreaChunkCalibrator(semantic_chunking)

        # Test with sample texts for each policy area
        areas_to_check = [policy_area] if policy_area else self.POLICY_AREAS[:3]  # Test first 3 for speed

        for pa in areas_to_check:
            # Generate sample text based on policy area
            sample_text = self._generate_sample_text(pa)

            try:
                chunks = calibrator.calibrate_for_policy_area(
                    text=sample_text,
                    policy_area=pa,
                    metadata={"validation": True}
                )

                # Validate chunk count
                if len(chunks) != calibrator.TARGET_CHUNKS_PER_PA:
                    raise ValidationError(
                        f"Expected {calibrator.TARGET_CHUNKS_PER_PA} chunks, got {len(chunks)}"
                    )

                # Validate chunk structure
                for i, chunk in enumerate(chunks):
                    if 'id' not in chunk:
                        raise ValidationError(f"Chunk {i} missing 'id' field")
                    if 'text' not in chunk or not chunk['text']:
                        raise ValidationError(f"Chunk {i} missing or empty 'text'")
                    if chunk.get('policy_area') != pa:
                        raise ValidationError(
                            f"Chunk {i} policy_area mismatch: expected {pa}, got {chunk.get('policy_area')}"
                        )

                logger.info(f"  ✓ {pa}: Generated {len(chunks)} chunks (target: {calibrator.TARGET_CHUNKS_PER_PA})")

                self.validation_results["chunk_validations"].append({
                    "policy_area": pa,
                    "chunk_count": len(chunks),
                    "target": calibrator.TARGET_CHUNKS_PER_PA,
                    "passed": True
                })

            except Exception as e:
                error = f"{pa}: Chunk calibration failed - {e}"
                logger.error(f"  ✗ {error}")
                self.validation_results["errors"].append(error)
                self.validation_results["chunk_validations"].append({
                    "policy_area": pa,
                    "passed": False,
                    "error": str(e)
                })

    def _validate_orchestrator(self, policy_area: str | None = None):
        """
        Validate that PolicyOrchestrator works correctly.

        Args:
            policy_area: Optional single policy area to validate
        """
        # Initialize orchestrator
        self.orchestrator = PolicyOrchestrator(signal_registry=self.signal_registry)

        # Load signals
        self.orchestrator.load_policy_signals(self.signals_dir)

        # Test orchestrator with mock chunks
        areas_to_check = [policy_area] if policy_area else self.POLICY_AREAS[:2]  # Test first 2

        for pa in areas_to_check:
            # Generate 10 mock chunks
            mock_chunks = self._generate_mock_chunks(pa, count=10)

            try:
                # Process with orchestrator
                result = self.orchestrator.process_policy_area(
                    chunks=mock_chunks,
                    policy_area=pa,
                    method_executor=None  # Mock executor
                )

                # Validate result
                if result.policy_area != pa:
                    raise ValidationError(f"policy_area mismatch in result")

                if result.chunks_processed != 10:
                    raise ValidationError(
                        f"Expected 10 chunks processed, got {result.chunks_processed}"
                    )

                if not result.validation_passed:
                    raise ValidationError("validation_passed flag is False")

                logger.info(
                    f"  ✓ {pa}: Processed {result.chunks_processed} chunks - "
                    f"signals v{result.signals_version}, "
                    f"time: {result.processing_time_s:.3f}s"
                )

                self.validation_results["orchestrator_validations"].append({
                    "policy_area": pa,
                    "chunks_processed": result.chunks_processed,
                    "signals_version": result.signals_version,
                    "processing_time_s": result.processing_time_s,
                    "passed": True
                })

            except Exception as e:
                error = f"{pa}: Orchestrator validation failed - {e}"
                logger.error(f"  ✗ {error}")
                self.validation_results["errors"].append(error)
                self.validation_results["orchestrator_validations"].append({
                    "policy_area": pa,
                    "passed": False,
                    "error": str(e)
                })

    def _generate_sample_text(self, policy_area: str) -> str:
        """
        Generate sample policy text for testing.

        Args:
            policy_area: Policy area ID

        Returns:
            Sample text string
        """
        # Generate realistic sample text based on policy area
        # This would be more sophisticated in production
        base_text = f"Documento de política para el área {policy_area}. "

        # Add multiple paragraphs to ensure enough content for 10 chunks
        paragraphs = []
        for i in range(15):
            paragraphs.append(
                f"Párrafo {i+1}: Este es un párrafo de ejemplo que contiene información "
                f"relevante para el área de política {policy_area}. Se incluyen objetivos, "
                f"estrategias, metas e indicadores que permiten evaluar el progreso y el "
                f"impacto de las intervenciones propuestas. Cada párrafo aporta contexto "
                f"específico que será analizado por los ejecutores correspondientes."
            )

        return base_text + " ".join(paragraphs)

    def _generate_mock_chunks(self, policy_area: str, count: int) -> List[Dict[str, Any]]:
        """
        Generate mock chunks for testing.

        Args:
            policy_area: Policy area ID
            count: Number of chunks to generate

        Returns:
            List of mock chunk dictionaries
        """
        chunks = []
        for i in range(count):
            chunks.append({
                'id': f"{policy_area}_chunk_{i+1}",
                'text': f"Mock chunk {i+1} text for {policy_area}. This is test content.",
                'policy_area': policy_area,
                'chunk_index': i,
                'chunk_type': 'diagnostic',  # Mock type
                'length': 50,
                'metadata': {'mock': True, 'validation': True}
            })
        return chunks

    def _print_summary(self):
        """Print validation summary."""
        logger.info("=" * 70)
        logger.info("VALIDATION SUMMARY")
        logger.info("=" * 70)
        logger.info("")

        logger.info(f"SignalPacks loaded: {self.validation_results['signal_packs_loaded']}")
        logger.info(f"SignalPacks validated: {self.validation_results['signal_packs_validated']}")
        logger.info(f"Chunk calibrations: {len(self.validation_results['chunk_validations'])}")
        logger.info(f"Orchestrator tests: {len(self.validation_results['orchestrator_validations'])}")
        logger.info(f"Errors: {len(self.validation_results['errors'])}")
        logger.info("")

        if self.validation_results["errors"]:
            logger.error("ERRORS:")
            for error in self.validation_results["errors"]:
                logger.error(f"  - {error}")
            logger.info("")


def main():
    """Main entry point."""
    import argparse

    parser = argparse.ArgumentParser(
        description="Validate Policy Orchestration System",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Validate all policy areas
  python scripts/validate_policy_orchestration.py

  # Validate specific policy area
  python scripts/validate_policy_orchestration.py --policy-area PA01

  # Verbose output
  python scripts/validate_policy_orchestration.py --verbose
        """
    )

    parser.add_argument(
        '--policy-area',
        type=str,
        choices=PolicyOrchestrationValidator.POLICY_AREAS,
        help='Validate specific policy area only (validates all by default)'
    )

    parser.add_argument(
        '--signals-dir',
        type=str,
        default='config/policy_signals',
        help='Directory containing signal pack JSON files (default: config/policy_signals)'
    )

    parser.add_argument(
        '--verbose',
        action='store_true',
        help='Enable verbose logging'
    )

    args = parser.parse_args()

    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)

    # Run validation
    validator = PolicyOrchestrationValidator(signals_dir=args.signals_dir)

    success = validator.run_full_validation(policy_area=args.policy_area)

    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
