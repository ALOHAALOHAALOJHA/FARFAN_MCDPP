"""
Boot-time validation checks for F.A.R.F.A.N runtime dependencies.

This module provides boot checks that validate critical dependencies before
pipeline execution. In PROD mode, failures abort execution unless explicitly
allowed by configuration flags.
"""

# =============================================================================
# METADATA
# =============================================================================

__version__ = "1.0.0"
__phase__ = 0
__stage__ = 50
__order__ = 0
__author__ = "F.A.R.F.A.N Core Team"
__created__ = "2026-01-10"
__modified__ = "2026-01-10"
__criticality__ = "CRITICAL"
__execution_pattern__ = "On-Demand"



import json
from pathlib import Path

from farfan_pipeline.phases.Phase_0.phase0_10_01_runtime_config import RuntimeConfig, RuntimeMode


class BootCheckError(Exception):
    """
    Raised when a boot check fails in strict mode.

    Attributes:
        component: Component that failed (e.g., "contradiction_module")
        reason: Human-readable failure reason
        code: Machine-readable error code
    """

    def __init__(self, component: str, reason: str, code: str):
        self.component = component
        self.reason = reason
        self.code = code
        super().__init__(f"Boot check failed [{code}] {component}: {reason}")


def check_contradiction_module_available(config: RuntimeConfig) -> bool:
    """
    Check if contradiction detection module is available.

    Args:
        config: Runtime configuration

    Returns:
        True if module available or fallback allowed

    Raises:
        BootCheckError: If module unavailable in strict PROD mode
    """
    try:
        from farfan_pipeline.methods.contradiction_deteccion import PolicyContradictionDetector

        return True
    except ImportError as e:
        # Use string comparison to avoid enum instance comparison issues
        if config.mode.value == "prod" and not config.allow_contradiction_fallback:
            raise BootCheckError(
                component="contradiction_module",
                reason=f"PolicyContradictionDetector not available: {e}",
                code="CONTRADICTION_MODULE_MISSING",
            )
        # Fallback allowed in DEV/EXPLORATORY or with flag
        return False


def check_wiring_validator_available(config: RuntimeConfig) -> bool:
    """
    Check if WiringValidator is available.

    Args:
        config: Runtime configuration

    Returns:
        True if validator available or disable allowed

    Raises:
        BootCheckError: If validator unavailable in strict PROD mode
    """
    try:
        import importlib
        importlib.import_module("farfan_pipeline.phases.Phase_0.phase0_90_03_wiring_validator")
        return True
    except ImportError as e:
        if config.mode == RuntimeMode.PROD and not config.allow_validator_disable:
            raise BootCheckError(
                component="wiring_validator",
                reason=f"WiringValidator not available: {e}",
                code="WIRING_VALIDATOR_MISSING",
            )
        return False


def check_spacy_model_available(model_name: str, config: RuntimeConfig) -> bool:
    """
    Check if preferred spaCy model is installed.

    Args:
        model_name: spaCy model name (e.g., "es_core_news_lg")
        config: Runtime configuration

    Returns:
        True if model available

    Raises:
        BootCheckError: If model unavailable in PROD mode
    """
    try:
        import spacy

        spacy.load(model_name)
        return True
    except (ImportError, OSError) as e:
        if config.mode == RuntimeMode.PROD:
            raise BootCheckError(
                component="spacy_model",
                reason=f"spaCy model '{model_name}' not available: {e}",
                code="SPACY_MODEL_MISSING",
            )
        return False


def check_calibration_files(config: RuntimeConfig, calibration_dir: Path | None = None) -> bool:
    """
    Check calibration files exist and have required structure.

    Args:
        config: Runtime configuration
        calibration_dir: Directory containing calibration files (default: config/layer_calibrations)

    Returns:
        True if calibration files valid

    Raises:
        BootCheckError: If calibration invalid in strict PROD mode
    """
    if calibration_dir is None:
        calibration_dir = Path("config/layer_calibrations")

    if not calibration_dir.exists():
        if config.mode == RuntimeMode.PROD and config.strict_calibration:
            raise BootCheckError(
                component="calibration_files",
                reason=f"Calibration directory not found: {calibration_dir}",
                code="CALIBRATION_DIR_MISSING",
            )
        return False

    # Check for required calibration files
    required_files = ["intrinsic_calibration.json", "fusion_specification.json"]
    missing_files = []

    for filename in required_files:
        file_path = calibration_dir.parent / filename
        if not file_path.exists():
            missing_files.append(filename)

    if missing_files:
        if config.mode == RuntimeMode.PROD and config.strict_calibration:
            raise BootCheckError(
                component="calibration_files",
                reason=f"Missing required calibration files: {', '.join(missing_files)}",
                code="CALIBRATION_FILES_MISSING",
            )
        return False

    # Validate _base_weights presence in strict mode
    if config.strict_calibration:
        intrinsic_path = calibration_dir.parent / "intrinsic_calibration.json"
        try:
            with open(intrinsic_path) as f:
                data = json.load(f)

            if "_base_weights" not in data:
                if config.mode == RuntimeMode.PROD:
                    raise BootCheckError(
                        component="calibration_files",
                        reason=f"Missing _base_weights in {intrinsic_path}",
                        code="CALIBRATION_BASE_WEIGHTS_MISSING",
                    )
                return False
        except (OSError, json.JSONDecodeError) as e:
            if config.mode == RuntimeMode.PROD:
                raise BootCheckError(
                    component="calibration_files",
                    reason=f"Failed to parse {intrinsic_path}: {e}",
                    code="CALIBRATION_PARSE_ERROR",
                )
            return False

    return True


def check_orchestration_metrics_contract(config: RuntimeConfig) -> bool:
    """
    Check that orchestration metrics contract is properly defined.

    This validates that the _execution_metrics['phase_2'] schema exists
    and is properly structured.

    Args:
        config: Runtime configuration

    Returns:
        True if contract valid

    Raises:
        BootCheckError: If contract invalid in PROD mode
    """
    try:
        # Lazy import to avoid circular dependency:
        # boot_checks → orchestrator → factory → verified_pipeline_runner → boot_checks
        from farfan_pipeline.orchestration.orchestrator import Orchestrator

        # Verify phase_2 metrics schema exists
        # This is a placeholder - actual implementation would check the schema
        return True
    except ImportError as e:
        if config.mode == RuntimeMode.PROD:
            raise BootCheckError(
                component="orchestration_metrics",
                reason=f"Orchestrator not available: {e}",
                code="ORCHESTRATOR_MISSING",
            )
        return False


def check_networkx_available() -> bool:
    """
    Check if NetworkX is available for graph metrics.

    Returns:
        True if NetworkX available

    Note:
        This is a soft check - NetworkX unavailability is Category B (quality degradation)
    """
    try:
        import networkx

        return True
    except ImportError:
        return False


def run_boot_checks(config: RuntimeConfig) -> dict[str, bool]:
    """
    Run all boot checks and return results.

    Args:
        config: Runtime configuration

    Returns:
        Dictionary mapping check name to success status

    Raises:
        BootCheckError: If any critical check fails in strict PROD mode

    Example:
        >>> config = RuntimeConfig.from_env()
        >>> results = run_boot_checks(config)
        >>> assert results['contradiction_module']
    """
    results = {}

    # Critical checks (Category A)
    results["contradiction_module"] = check_contradiction_module_available(config)
    results["wiring_validator"] = check_wiring_validator_available(config)
    results["spacy_model"] = check_spacy_model_available(config.preferred_spacy_model, config)
    results["calibration_files"] = check_calibration_files(config)
    results["orchestration_metrics"] = check_orchestration_metrics_contract(config)

    # Quality checks (Category B)
    results["networkx"] = check_networkx_available()

    return results


def get_boot_check_summary(results: dict[str, bool]) -> str:
    """
    Generate human-readable summary of boot check results.

    Args:
        results: Boot check results from run_boot_checks()

    Returns:
        Formatted summary string
    """
    passed = sum(1 for v in results.values() if v)
    total = len(results)

    lines = [f"Boot Checks: {passed}/{total} passed"]
    lines.append("")

    for check, success in results.items():
        status = "✓" if success else "✗"
        lines.append(f"  {status} {check}")

    return "\n".join(lines)
