"""
Integration Example: Phase 11 (Contract Quality) in Orchestrator

This example demonstrates how to integrate Phase 11 into the orchestrator.
"""

from pathlib import Path
from typing import Any, Dict
from farfan_pipeline.phases.Phase_contract_quality import (
    ContractQualityPhase,
    ContractQualityResult,
)


def integrate_phase_11_into_orchestrator() -> None:
    """
    Example integration of Phase 11 into the F.A.R.F.A.N orchestrator.
    
    Steps:
    1. Add phase to FASES list
    2. Implement handler method
    3. Configure phase parameters
    """
    
    # STEP 1: Add to FASES list in orchestrator
    # ------------------------------------------
    # FASES: list[tuple[int, str, str, str]] = [
    #     # ... existing phases 0-10 ...
    #     (11, "sync", "_validate_contract_quality", "FASE 11 - Calidad de Contratos"),
    # ]
    
    # STEP 2: Add phase configuration
    # --------------------------------
    # PHASE_TIMEOUTS = {
    #     # ... existing phases ...
    #     11: 300.0,  # 5 minutes for ~300 contracts
    # }
    #
    # PHASE_OUTPUT_KEYS = {
    #     # ... existing phases ...
    #     11: "contract_quality_result",
    # }
    #
    # PHASE_ARGUMENT_KEYS = {
    #     # ... existing phases ...
    #     11: ["config"],
    # }
    
    print("Phase 11 integration configuration ready")


async def _validate_contract_quality_handler(
    context: Dict[str, Any],
    config: Any,  # RuntimeConfig type
) -> ContractQualityResult:
    """
    Phase 11 Handler: Contract Quality Validation
    
    This is the handler method that would be added to the Orchestrator class.
    
    Args:
        context: Pipeline execution context
        config: Runtime configuration
        
    Returns:
        ContractQualityResult with evaluation outcomes
        
    Raises:
        RuntimeError: If contracts directory not found or invalid
    """
    from pathlib import Path
    import structlog
    
    logger = structlog.get_logger(__name__)
    
    # Get contracts directory from Phase 2
    contracts_dir = Path(
        "src/farfan_pipeline/phases/Phase_two/"
        "json_files_phase_two/executor_contracts/specialized"
    )
    
    # Create output directory
    output_dir = Path("reports/contract_quality")
    
    # Initialize phase
    phase = ContractQualityPhase(contracts_dir, output_dir)
    
    # Validate input
    if not phase.validate_input(context):
        raise RuntimeError(
            "Phase 11: Invalid input - contracts directory not found or empty"
        )
    
    logger.info(
        "Phase 11: Starting contract quality validation",
        contracts_dir=str(contracts_dir),
        output_dir=str(output_dir),
    )
    
    # Execute phase
    result = phase.execute(
        contract_range=(1, 300),
        config=context.get("config")
    )
    
    # Log results
    logger.info(
        "Phase 11: Contract quality validation complete",
        contracts_evaluated=result.contracts_evaluated,
        average_score=result.average_score,
        production_ready=result.production_ready,
        need_patches=result.need_patches,
        need_reformulation=result.need_reformulation,
    )
    
    # Quality gate check
    production_rate = (
        result.production_ready / result.contracts_evaluated 
        if result.contracts_evaluated > 0 
        else 0
    )
    
    if production_rate < 0.8:
        logger.warning(
            "Phase 11: Quality gate warning",
            production_rate=production_rate,
            threshold=0.8,
            message="Less than 80% of contracts are production-ready",
        )
    else:
        logger.info(
            "Phase 11: Quality gate passed",
            production_rate=production_rate,
        )
    
    return result


def standalone_phase_execution_example() -> None:
    """
    Example: Running Phase 11 standalone (outside orchestrator).
    
    This is useful for:
    - Contract auditing
    - Quality monitoring
    - Development/testing
    """
    from pathlib import Path
    
    # Setup paths
    contracts_dir = Path(
        "src/farfan_pipeline/phases/Phase_two/"
        "json_files_phase_two/executor_contracts/specialized"
    )
    output_dir = Path("reports/contract_quality")
    
    # Initialize phase
    phase = ContractQualityPhase(contracts_dir, output_dir)
    
    # Execute on specific range (e.g., first batch)
    result = phase.execute(contract_range=(1, 25))
    
    # Print results
    print(f"Evaluated: {result.contracts_evaluated} contracts")
    print(f"Average Score: {result.average_score:.1f}/100")
    print(f"Production Ready: {result.production_ready}")
    print(f"Need Patches: {result.need_patches}")
    print(f"Need Reformulation: {result.need_reformulation}")
    print(f"Report saved: {result.summary_report_path}")


def get_phase_contract_specification() -> Dict[str, Any]:
    """
    Get Phase 11 contract specification programmatically.
    
    Returns:
        Phase contract dictionary
    """
    from pathlib import Path
    
    # Initialize phase
    contracts_dir = Path("src/farfan_pipeline/phases/Phase_two/json_files_phase_two/executor_contracts/specialized")
    output_dir = Path("reports/contract_quality")
    phase = ContractQualityPhase(contracts_dir, output_dir)
    
    # Get contract specification
    contract_spec = phase.get_phase_contract()
    
    return contract_spec


if __name__ == "__main__":
    print("=" * 80)
    print("Phase 11 (Contract Quality) Integration Examples")
    print("=" * 80)
    print()
    
    # Example 1: Integration configuration
    print("1. Orchestrator Integration Configuration")
    print("-" * 80)
    integrate_phase_11_into_orchestrator()
    print()
    
    # Example 2: Get contract specification
    print("2. Phase Contract Specification")
    print("-" * 80)
    contract_spec = get_phase_contract_specification()
    print(f"Phase ID: {contract_spec['phase_id']}")
    print(f"Phase Name: {contract_spec['phase_name']}")
    print(f"Phase Mode: {contract_spec['phase_mode']}")
    print(f"Ignition: {contract_spec['ignition_point']['trigger']}")
    print()
    
    # Example 3: Standalone execution (commented out - requires actual contracts)
    # print("3. Standalone Execution Example")
    # print("-" * 80)
    # standalone_phase_execution_example()
    
    print("=" * 80)
    print("Integration examples complete!")
    print("=" * 80)
