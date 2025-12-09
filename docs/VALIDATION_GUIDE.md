# F.A.R.F.A.N Validation Guide

**How to Validate System Integrity and Reproducibility**

Version: 1.0.0  
Last Updated: 2024-12-16

---

## Table of Contents

1. [Overview](#overview)
2. [Pre-Execution Validation](#pre-execution-validation)
3. [Runtime Validation](#runtime-validation)
4. [Post-Execution Validation](#post-execution-validation)
5. [Determinism Validation](#determinism-validation)
6. [Calibration Validation](#calibration-validation)
7. [Automated Validation Suite](#automated-validation-suite)

---

## Overview

System validation ensures F.A.R.F.A.N operates correctly, deterministically, and produces trustworthy results. This guide covers validation procedures at all stages of execution.

### Validation Levels

1. **Phase 0 (Bootstrap)**: Configuration integrity, file hashes, seed initialization
2. **Runtime**: Contract compliance, chain integrity, threshold enforcement
3. **Post-execution**: Output verification, HMAC signatures, reproducibility
4. **Calibration**: Method quality scores, weight normalization, threshold alignment

---

## Pre-Execution Validation

### Configuration Integrity Check

```python
def validate_configuration_integrity() -> bool:
    """
    Validate all configuration files before execution.
    
    Returns:
        True if all checks pass
    """
    import json
    import hashlib
    from pathlib import Path
    
    # 1. Verify cohort consistency
    calibration_dir = Path("src/cross_cutting_infrastrucuture/capaz_calibration_parmetrization/calibration")
    
    cohort_files = list(calibration_dir.glob("COHORT_2024_*.json"))
    cohorts = set()
    
    for file_path in cohort_files:
        with open(file_path) as f:
            data = json.load(f)
            cohorts.add(data["_cohort_metadata"]["cohort_id"])
    
    if len(cohorts) != 1:
        print(f"ERROR: Inconsistent cohorts: {cohorts}")
        return False
    
    print(f"✓ Cohort consistency: {cohorts.pop()}")
    
    # 2. Compute file hashes
    manifest_path = calibration_dir.parent / "COHORT_MANIFEST.json"
    
    if not manifest_path.exists():
        print("ERROR: COHORT_MANIFEST.json not found")
        return False
    
    with open(manifest_path) as f:
        manifest = json.load(f)
    
    # 3. Verify hashes match manifest
    for file_key, file_info in manifest.get("files", {}).items():
        file_path = Path(file_info["path"])
        expected_hash = file_info["hash"]
        
        # Compute actual hash
        hasher = hashlib.sha256()
        with open(file_path, 'rb') as f:
            hasher.update(f.read())
        actual_hash = f"sha256:{hasher.hexdigest()}"
        
        if actual_hash != expected_hash:
            print(f"ERROR: Hash mismatch for {file_path}")
            print(f"  Expected: {expected_hash}")
            print(f"  Actual:   {actual_hash}")
            return False
    
    print("✓ File integrity verified")
    
    # 4. Validate fusion weights normalization
    with open(calibration_dir / "COHORT_2024_fusion_weights.json") as f:
        fusion_data = json.load(f)
    
    for role, params in fusion_data["role_fusion_parameters"].items():
        linear_sum = sum(params["linear_weights"].values())
        interaction_sum = sum(params["interaction_weights"].values())
        total = linear_sum + interaction_sum
        
        if abs(total - 1.0) > 1e-6:
            print(f"ERROR: Weights for role {role} sum to {total}, expected 1.0")
            return False
    
    print("✓ Fusion weights normalized")
    
    return True
```

**Run before execution**:
```bash
python -c "
from validation import validate_configuration_integrity
if not validate_configuration_integrity():
    exit(1)
"
```

---

### Seed Registry Validation

```python
def validate_seed_registry(base_seed: int = 42) -> bool:
    """Validate deterministic seed generation."""
    from src.orchestration.seed_registry import SeedRegistry
    
    # Create two registries with same base seed
    registry1 = SeedRegistry(base_seed=base_seed)
    registry2 = SeedRegistry(base_seed=base_seed)
    
    # Generate seeds for same operations
    ops = ["phase0", "phase1_chunking", "phase2_D1_Q1", "phase3_scoring"]
    
    for op in ops:
        seed1 = registry1.get_seed(op)
        seed2 = registry2.get_seed(op)
        
        if seed1 != seed2:
            print(f"ERROR: Seed mismatch for {op}: {seed1} != {seed2}")
            return False
    
    print("✓ Seed registry deterministic")
    
    # Verify seed derivation is unique per operation
    seeds = [registry1.get_seed(op) for op in ops]
    
    if len(seeds) != len(set(seeds)):
        print("ERROR: Duplicate seeds detected")
        return False
    
    print("✓ Seed uniqueness verified")
    
    return True
```

---

## Runtime Validation

### Contract Validation

```python
def validate_executor_output(
    executor_id: str,
    output: dict,
    contract_spec: dict
) -> tuple[bool, list[str]]:
    """
    Validate executor output against contract.
    
    Returns:
        (is_valid, list_of_violations)
    """
    violations = []
    
    # 1. Check required fields
    for field in contract_spec["required_fields"]:
        if field not in output:
            violations.append(f"Missing required field: {field}")
    
    # 2. Check types
    for field, expected_type in contract_spec["types"].items():
        if field in output:
            actual_type = type(output[field]).__name__
            if actual_type != expected_type:
                violations.append(
                    f"Type mismatch for {field}: expected {expected_type}, got {actual_type}"
                )
    
    # 3. Check score range
    if "score" in output:
        if not (0.0 <= output["score"] <= 1.0):
            violations.append(f"Score out of range: {output['score']}")
    
    # 4. Check confidence range
    if "confidence" in output:
        if not (0.0 <= output["confidence"] <= 1.0):
            violations.append(f"Confidence out of range: {output['confidence']}")
    
    # 5. Check provenance completeness
    if "provenance" in output:
        required_prov = ["method_id", "method_version", "cohort", "seed"]
        for field in required_prov:
            if field not in output["provenance"]:
                violations.append(f"Provenance missing: {field}")
    
    is_valid = len(violations) == 0
    
    if is_valid:
        print(f"✓ Contract validation passed for {executor_id}")
    else:
        print(f"✗ Contract validation failed for {executor_id}")
        for v in violations:
            print(f"  - {v}")
    
    return is_valid, violations
```

---

### Chain Integrity Validation

```python
def validate_chain_integrity(
    phase_results: dict,
    expected_chain: list
) -> bool:
    """
    Validate data flow chain integrity.
    
    Args:
        phase_results: Results from each phase
        expected_chain: Expected phase execution order
    
    Returns:
        True if chain is intact
    """
    # 1. Verify all phases completed
    for phase in expected_chain:
        if phase not in phase_results:
            print(f"ERROR: Phase {phase} missing from results")
            return False
    
    print("✓ All phases completed")
    
    # 2. Verify temporal ordering
    timestamps = {
        phase: phase_results[phase]["timestamp"]
        for phase in expected_chain
    }
    
    for i in range(len(expected_chain) - 1):
        phase_current = expected_chain[i]
        phase_next = expected_chain[i + 1]
        
        if timestamps[phase_current] >= timestamps[phase_next]:
            print(f"ERROR: Temporal ordering violated: {phase_current} -> {phase_next}")
            return False
    
    print("✓ Temporal ordering verified")
    
    # 3. Verify provenance chain
    for i in range(1, len(expected_chain)):
        phase = expected_chain[i]
        result = phase_results[phase]
        
        if "provenance" not in result:
            print(f"ERROR: Phase {phase} missing provenance")
            return False
        
        # Check that provenance references previous phase
        prov = result["provenance"]
        if "dependencies" in prov:
            prev_phase = expected_chain[i - 1]
            if prev_phase not in prov["dependencies"]:
                print(f"WARNING: Phase {phase} does not reference {prev_phase}")
    
    print("✓ Provenance chain intact")
    
    return True
```

---

### Threshold Enforcement Validation

```python
def validate_threshold_enforcement(
    executor_results: dict,
    thresholds: dict
) -> bool:
    """
    Validate that hard gates are properly enforced.
    
    Args:
        executor_results: Results from all executors
        thresholds: Hard gate thresholds
    
    Returns:
        True if thresholds properly enforced
    """
    violations = []
    
    for executor_id, result in executor_results.items():
        # Check @b hard gate
        if result["@b"] < thresholds["@b"]["hard_gate"]:
            if result["status"] != "failed":
                violations.append(
                    f"{executor_id}: @b={result['@b']} < {thresholds['@b']['hard_gate']} "
                    f"but status={result['status']} (should be 'failed')"
                )
        
        # Check @chain hard gate
        if result["@chain"] == 0.0:
            if result["status"] != "aborted":
                violations.append(
                    f"{executor_id}: @chain=0.0 but status={result['status']} "
                    f"(should be 'aborted')"
                )
        
        # Check @C hard gate
        if result["@C"] < thresholds["@C"]["hard_gate"]:
            if result["status"] != "failed":
                violations.append(
                    f"{executor_id}: @C={result['@C']} < {thresholds['@C']['hard_gate']} "
                    f"but status={result['status']} (should be 'failed')"
                )
    
    if violations:
        print("✗ Threshold enforcement failures:")
        for v in violations:
            print(f"  - {v}")
        return False
    
    print("✓ Hard gates properly enforced")
    return True
```

---

## Post-Execution Validation

### Output Verification

```python
def validate_output_artifacts(output_dir: Path) -> bool:
    """
    Validate all output artifacts exist and are well-formed.
    
    Args:
        output_dir: Directory containing output files
    
    Returns:
        True if all artifacts valid
    """
    import json
    
    # Expected artifacts
    expected_files = [
        "micro_report.json",
        "meso_report.json",
        "macro_report.json",
        "verification_manifest.json",
    ]
    
    # 1. Check file existence
    for file_name in expected_files:
        file_path = output_dir / file_name
        if not file_path.exists():
            print(f"ERROR: Missing artifact: {file_name}")
            return False
    
    print("✓ All artifacts present")
    
    # 2. Validate JSON structure
    for file_name in expected_files:
        file_path = output_dir / file_name
        try:
            with open(file_path) as f:
                data = json.load(f)
        except json.JSONDecodeError as e:
            print(f"ERROR: Invalid JSON in {file_name}: {e}")
            return False
    
    print("✓ All artifacts well-formed")
    
    # 3. Validate report completeness
    with open(output_dir / "micro_report.json") as f:
        micro = json.load(f)
    
    # Check all 300 questions covered
    expected_questions = 300
    actual_questions = len(micro.get("responses", {}))
    
    if actual_questions != expected_questions:
        print(f"WARNING: Micro report has {actual_questions} responses, expected {expected_questions}")
    
    print(f"✓ Micro report completeness: {actual_questions}/300 questions")
    
    return True
```

---

### HMAC Signature Verification

```python
def validate_verification_manifest(
    manifest_path: Path,
    hmac_secret: str
) -> bool:
    """
    Validate HMAC signature of verification manifest.
    
    Args:
        manifest_path: Path to verification_manifest.json
        hmac_secret: HMAC secret key
    
    Returns:
        True if signature valid
    """
    import json
    import hmac
    import hashlib
    
    # Load manifest
    with open(manifest_path) as f:
        manifest = json.load(f)
    
    # Extract signature
    if "integrity" not in manifest:
        print("ERROR: No integrity section in manifest")
        return False
    
    recorded_signature = manifest["integrity"]["signature"]
    
    # Rebuild manifest without signature
    manifest_without_sig = manifest.copy()
    del manifest_without_sig["integrity"]
    
    # Compute expected signature
    canonical = json.dumps(manifest_without_sig, sort_keys=True, separators=(',', ':'))
    expected_signature = hmac.new(
        key=hmac_secret.encode('utf-8'),
        msg=canonical.encode('utf-8'),
        digestmod=hashlib.sha256
    ).hexdigest()
    
    # Compare
    if hmac.compare_digest(expected_signature, recorded_signature):
        print("✓ HMAC signature valid")
        return True
    else:
        print("✗ HMAC signature invalid - manifest may be tampered")
        print(f"  Expected: {expected_signature}")
        print(f"  Recorded: {recorded_signature}")
        return False
```

---

## Determinism Validation

### Reproducibility Test

```python
def validate_reproducibility(
    pdt_path: Path,
    questionnaire_path: Path,
    seed: int = 42,
    num_runs: int = 2
) -> bool:
    """
    Validate that pipeline produces identical results across runs.
    
    Args:
        pdt_path: Path to PDT file
        questionnaire_path: Path to questionnaire
        seed: Base seed for determinism
        num_runs: Number of test runs (default: 2)
    
    Returns:
        True if all runs produce identical outputs
    """
    import subprocess
    import hashlib
    
    output_hashes = []
    
    for run in range(num_runs):
        print(f"\n--- Run {run + 1}/{num_runs} ---")
        
        # Run pipeline
        output_dir = Path(f"output/reproducibility_test_run{run}")
        output_dir.mkdir(parents=True, exist_ok=True)
        
        cmd = [
            "python", "src/orchestration/orchestrator.py",
            "--pdt", str(pdt_path),
            "--questionnaire", str(questionnaire_path),
            "--seed", str(seed),
            "--output", str(output_dir),
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.returncode != 0:
            print(f"ERROR: Run {run + 1} failed")
            print(result.stderr)
            return False
        
        # Compute hash of output
        micro_report = output_dir / "micro_report.json"
        
        hasher = hashlib.sha256()
        with open(micro_report, 'rb') as f:
            hasher.update(f.read())
        
        output_hash = hasher.hexdigest()
        output_hashes.append(output_hash)
        
        print(f"Output hash: {output_hash}")
    
    # Compare hashes
    if len(set(output_hashes)) == 1:
        print("\n✓ Reproducibility validated - all runs identical")
        return True
    else:
        print("\n✗ Reproducibility failed - runs produced different outputs")
        for i, hash_val in enumerate(output_hashes):
            print(f"  Run {i + 1}: {hash_val}")
        return False
```

---

## Calibration Validation

### Method Quality Validation

```python
def validate_method_calibration(
    method_id: str,
    calibration_data: dict,
    validation_pdts: list
) -> bool:
    """
    Validate method calibration scores against empirical data.
    
    Args:
        method_id: Method to validate
        calibration_data: Calibration scores
        validation_pdts: Validation PDT set
    
    Returns:
        True if calibration is valid
    """
    from src.methods_dispensary import get_method
    
    method = get_method(method_id)
    
    # 1. Verify @b components
    b_theory = calibration_data["b_theory"]
    b_impl = calibration_data["b_impl"]
    b_deploy = calibration_data["b_deploy"]
    b_overall = calibration_data["b_overall"]
    
    # Check aggregation
    expected_overall = (b_theory + b_impl + b_deploy) / 3
    if abs(b_overall - expected_overall) > 1e-6:
        print(f"ERROR: @b aggregation incorrect")
        print(f"  Expected: {expected_overall:.4f}")
        print(f"  Recorded: {b_overall:.4f}")
        return False
    
    print("✓ @b aggregation correct")
    
    # 2. Empirical validation of b_deploy
    results = []
    failures = 0
    
    for pdt in validation_pdts:
        try:
            result = method.execute(pdt)
            results.append(result.score)
        except Exception:
            failures += 1
    
    # Check failure rate
    failure_rate = failures / (len(results) + failures)
    expected_failure_rate = 0.01 if b_deploy >= 0.9 else 0.05
    
    if failure_rate > expected_failure_rate:
        print(f"WARNING: Failure rate {failure_rate:.2%} exceeds calibration expectation")
    
    # Check stability (CV)
    import numpy as np
    cv = np.std(results) / np.mean(results) if results else float('inf')
    expected_cv = 0.05 if b_deploy >= 0.9 else 0.10
    
    if cv > expected_cv:
        print(f"WARNING: CV {cv:.4f} exceeds calibration expectation {expected_cv:.4f}")
    
    print(f"✓ Empirical validation: failure_rate={failure_rate:.2%}, CV={cv:.4f}")
    
    return True
```

---

## Automated Validation Suite

### Complete Validation Pipeline

```python
def run_full_validation_suite(
    config_dir: Path,
    test_pdt: Path,
    test_questionnaire: Path,
    hmac_secret: str,
    num_reproducibility_runs: int = 2
) -> bool:
    """
    Run complete validation suite.
    
    Returns:
        True if all validations pass
    """
    print("=" * 60)
    print("F.A.R.F.A.N Validation Suite")
    print("=" * 60)
    
    # 1. Pre-execution validation
    print("\n[1/5] Pre-Execution Validation")
    print("-" * 60)
    
    if not validate_configuration_integrity():
        print("✗ Configuration validation failed")
        return False
    
    if not validate_seed_registry():
        print("✗ Seed registry validation failed")
        return False
    
    # 2. Determinism validation
    print("\n[2/5] Determinism Validation")
    print("-" * 60)
    
    if not validate_reproducibility(
        test_pdt,
        test_questionnaire,
        num_runs=num_reproducibility_runs
    ):
        print("✗ Reproducibility validation failed")
        return False
    
    # 3. Runtime validation
    print("\n[3/5] Runtime Validation")
    print("-" * 60)
    
    # Run pipeline and capture results
    # (implementation depends on orchestrator API)
    
    # 4. Post-execution validation
    print("\n[4/5] Post-Execution Validation")
    print("-" * 60)
    
    output_dir = Path("output/validation_test")
    
    if not validate_output_artifacts(output_dir):
        print("✗ Output validation failed")
        return False
    
    if not validate_verification_manifest(
        output_dir / "verification_manifest.json",
        hmac_secret
    ):
        print("✗ HMAC validation failed")
        return False
    
    # 5. Calibration validation
    print("\n[5/5] Calibration Validation")
    print("-" * 60)
    
    # (Requires validation PDT set)
    
    print("\n" + "=" * 60)
    print("✓ ALL VALIDATIONS PASSED")
    print("=" * 60)
    
    return True
```

**Run validation suite**:
```bash
python scripts/run_validation_suite.py \
  --config-dir src/cross_cutting_infrastrucuture/capaz_calibration_parmetrization/calibration \
  --test-pdt data/test/sample_pdt.pdf \
  --test-questionnaire config/questionnaire_monolith.json \
  --hmac-secret $VERIFICATION_HMAC_SECRET \
  --reproducibility-runs 3
```

---

## Related Documentation

- [DETERMINISM.md](./DETERMINISM.md) - Reproducibility guarantees
- [TROUBLESHOOTING.md](./TROUBLESHOOTING.md) - Common issues
- [THRESHOLD_GUIDE.md](./THRESHOLD_GUIDE.md) - Quality thresholds

---

**Last Updated**: 2024-12-16  
**Version**: 1.0.0  
**Maintainers**: Policy Analytics Research Unit
