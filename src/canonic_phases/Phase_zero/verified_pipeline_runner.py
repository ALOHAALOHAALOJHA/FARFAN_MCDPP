"""
Verified Pipeline Runner - Phase 0 Orchestrator
================================================

Implements the P00-EN v2.0 specification for pre-execution validation and
deterministic bootstrap. This is the CANONICAL Phase 0 orchestrator.

Architecture:
    Phase 0 consists of 4 strictly sequenced sub-phases with exit gates:
    
    P0.0: Bootstrap          → Runtime config, seed registry, manifest builder
    P0.1: Input Verification → Cryptographic hash validation (SHA-256)
    P0.2: Boot Checks        → Dependency validation (PROD: fatal, DEV: warn)
    P0.3: Determinism        → RNG seeding with mandatory python+numpy seeds
    
    EXIT GATE: self.errors MUST be empty ∧ _bootstrap_failed = False

Contract:
    - NEVER proceeds with partial configurations
    - NEVER uses defaults on config errors
    - ALWAYS fails fast and clean
    - ALWAYS generates failure manifest on abort

Questionnaire Access Architecture:
    Phase 0 ONLY validates questionnaire file integrity (SHA-256 hash).
    
    CRITICAL: Phase 0 does NOT load or parse questionnaire content.
    
    Questionnaire access hierarchy (per factory.py):
        Level 1: AnalysisPipelineFactory (ONLY owner, loads CanonicalQuestionnaire)
        Level 2: QuestionnaireResourceProvider (scoped access, no I/O)
        Level 3: Orchestrator (accesses via Provider)
        Level 4: Signals (alternative access path)
    
    Phase 0 validates FILE INTEGRITY only, NOT content. Factory loads after Phase 0 passes.

Author: Phase 0 Compliance Team
Version: 2.0.1
Specification: P00-EN v2.0
"""

from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path
from typing import Any

from canonic_phases.Phase_zero.boot_checks import BootCheckError, run_boot_checks
from canonic_phases.Phase_zero.determinism import initialize_determinism_from_registry
from canonic_phases.Phase_zero.exit_gates import (
    check_all_gates,
    get_gate_summary,
)
from canonic_phases.Phase_zero.runtime_config import RuntimeConfig


class VerifiedPipelineRunner:
    """
    Phase 0 orchestrator with strict contract enforcement.
    
    This class implements the complete Phase 0 validation sequence as specified
    in P00-EN v2.0. It MUST be the first component executed in the pipeline.
    
    Attributes:
        plan_pdf_path: Path to input policy plan PDF
        questionnaire_path: Path to questionnaire monolith JSON
        artifacts_dir: Directory for output artifacts
        execution_id: Unique execution identifier (timestamp-based)
        errors: List of accumulated errors (MUST be empty for success)
        _bootstrap_failed: Flag indicating bootstrap failure
        runtime_config: Validated runtime configuration
        seed_snapshot: Dictionary of applied seeds (populated in P0.3)
        input_pdf_sha256: SHA-256 hash of input PDF (populated in P0.1)
        questionnaire_sha256: SHA-256 hash of questionnaire (populated in P0.1)
    """
    
    def __init__(
        self,
        plan_pdf_path: Path,
        artifacts_dir: Path,
        questionnaire_path: Path,
    ):
        """
        P0.0: Bootstrap - Initialize core runner infrastructure.
        
        This method initializes runtime configuration, seed registry, and
        manifest builder. It does NOT seed RNGs (that happens in P0.3).
        
        CRITICAL: Phase 0 only validates file integrity (hashing).
                  Factory loads questionnaire AFTER Phase 0 passes.
        
        Args:
            plan_pdf_path: Path to input policy plan PDF
            artifacts_dir: Directory for output artifacts
            questionnaire_path: Path to questionnaire file for hash validation
                               (Factory will load content after Phase 0)
            
        Postconditions:
            - self.runtime_config set (or None with _bootstrap_failed=True)
            - self.artifacts_dir exists
            - self.seed_registry initialized
            - self.errors empty (or populated with bootstrap errors)
            - self._bootstrap_failed reflects init status
        """
        self.plan_pdf_path = plan_pdf_path
        self.artifacts_dir = artifacts_dir
        self.questionnaire_path = questionnaire_path  # For hash validation ONLY
        self.errors: list[str] = []
        self._bootstrap_failed: bool = False
        
        # Generate execution identifiers
        self.execution_id = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
        self.policy_unit_id = f"policy_unit::{self.plan_pdf_path.stem}"
        self.correlation_id = self.execution_id
        
        # Initialize seed registry (but don't seed yet - that's P0.3)
        from orchestration.seed_registry import get_global_seed_registry
        self.seed_registry = get_global_seed_registry()
        self.seed_snapshot: dict[str, int] = {}  # Populated in P0.3
        
        # Initialize attributes for P0.1
        self.input_pdf_sha256: str = ""
        self.questionnaire_sha256: str = ""
        
        # P0.0.1: Load runtime configuration
        self.runtime_config: RuntimeConfig | None = None
        try:
            self.runtime_config = RuntimeConfig.from_env()
            self._log_bootstrap("runtime_config_loaded", {
                "mode": self.runtime_config.mode.value,
                "strict": self.runtime_config.is_strict_mode(),
            })
        except Exception as e:
            self._log_bootstrap("runtime_config_failed", {"error": str(e)})
            self.errors.append(f"Failed to load runtime config: {e}")
            self._bootstrap_failed = True
        
        # P0.0.2: Create artifacts directory
        try:
            self.artifacts_dir.mkdir(parents=True, exist_ok=True)
            self._log_bootstrap("artifacts_dir_created", {
                "path": str(self.artifacts_dir)
            })
        except Exception as e:
            self._log_bootstrap("artifacts_dir_failed", {"error": str(e)})
            self.errors.append(f"Failed to create artifacts directory: {e}")
            self._bootstrap_failed = True
        
        # P0.0.3: Bootstrap complete
        if not self._bootstrap_failed:
            self._log_bootstrap("bootstrap_complete", {
                "execution_id": self.execution_id,
                "policy_unit_id": self.policy_unit_id,
            })
    
    def _log_bootstrap(self, event: str, data: dict[str, Any]) -> None:
        """Log bootstrap event (minimal logging during bootstrap)."""
        # In production, this would use structured logging
        # For now, we keep it simple
        print(f"[BOOTSTRAP] {event}: {data}", flush=True)
    
    def _compute_sha256_streaming(self, file_path: Path) -> str:
        """
        Compute SHA-256 hash of file using streaming read.
        
        Args:
            file_path: Path to file
            
        Returns:
            Hex-encoded SHA-256 hash
        """
        import hashlib
        sha256_hash = hashlib.sha256()
        with open(file_path, "rb") as f:
            for byte_block in iter(lambda: f.read(4096), b""):
                sha256_hash.update(byte_block)
        return sha256_hash.hexdigest()
    
    def verify_input(self, expected_hashes: dict[str, str] | None = None) -> bool:
        """
        P0.1: Input Verification - Hash and validate input files.
        
        Computes SHA-256 hashes for FILE INTEGRITY only:
        - Input policy plan PDF
        - Questionnaire monolith JSON (file integrity, NOT content parsing)
        
        CRITICAL: Phase 0 does NOT load or parse questionnaire content.
                  This validates FILE INTEGRITY only. Factory loads content
                  AFTER Phase 0 passes via load_questionnaire().
        
        Optionally validates against expected hashes for tamper detection.
        
        Args:
            expected_hashes: Optional dict with keys 'pdf' and 'questionnaire'
                            containing expected SHA-256 hashes (64-char hex)
        
        Returns:
            True if all inputs verified successfully
            
        Postconditions:
            - self.input_pdf_sha256 set (or error appended)
            - self.questionnaire_sha256 set (or error appended)
            - Files exist and are readable
            - Hashes match expected values (if provided)
            - Content NOT loaded (deferred to Factory)
            
        Specification:
            P00-EN v2.0 Section 3.2
        """
        print("[P0.1] Starting input verification", flush=True)
        
        if expected_hashes:
            print(f"[P0.1] Hash validation enabled (will verify against expected values)", flush=True)
        
        # Verify PDF exists and hash
        if not self.plan_pdf_path.exists():
            error = f"Input PDF not found: {self.plan_pdf_path}"
            self.errors.append(error)
            print(f"[P0.1] ERROR: {error}", flush=True)
            return False
        
        try:
            self.input_pdf_sha256 = self._compute_sha256_streaming(self.plan_pdf_path)
            print(f"[P0.1] PDF hashed: {self.input_pdf_sha256[:16]}...", flush=True)
        except Exception as e:
            error = f"Failed to hash PDF: {e}"
            self.errors.append(error)
            print(f"[P0.1] ERROR: {error}", flush=True)
            return False
        
        # Verify questionnaire file exists and hash (FILE INTEGRITY ONLY)
        # NOTE: Phase 0 does NOT parse content. Factory loads after Phase 0 passes.
        if not self.questionnaire_path.exists():
            error = f"Questionnaire file not found: {self.questionnaire_path}"
            self.errors.append(error)
            print(f"[P0.1] ERROR: {error}", flush=True)
            return False
        
        try:
            self.questionnaire_sha256 = self._compute_sha256_streaming(self.questionnaire_path)
            print(f"[P0.1] Questionnaire file hashed (integrity only): {self.questionnaire_sha256[:16]}...", flush=True)
            print(f"[P0.1] ℹ️  Content will be loaded by Factory after Phase 0 passes", flush=True)
        except Exception as e:
            error = f"Failed to hash questionnaire file: {e}"
            self.errors.append(error)
            print(f"[P0.1] ERROR: {error}", flush=True)
            return False
        
        # Optional: Validate against expected hashes (tamper detection)
        if expected_hashes:
            validation_passed = True
            
            if 'pdf' in expected_hashes:
                expected_pdf = expected_hashes['pdf']
                if self.input_pdf_sha256 != expected_pdf:
                    error = (
                        f"PDF hash mismatch! "
                        f"Expected: {expected_pdf[:16]}... "
                        f"Got: {self.input_pdf_sha256[:16]}... "
                        f"(possible tampering detected)"
                    )
                    self.errors.append(error)
                    print(f"[P0.1] ERROR: {error}", flush=True)
                    validation_passed = False
                else:
                    print(f"[P0.1] ✓ PDF hash validated against expected value", flush=True)
            
            if 'questionnaire' in expected_hashes:
                expected_q = expected_hashes['questionnaire']
                if self.questionnaire_sha256 != expected_q:
                    error = (
                        f"Questionnaire hash mismatch! "
                        f"Expected: {expected_q[:16]}... "
                        f"Got: {self.questionnaire_sha256[:16]}... "
                        f"(possible tampering detected)"
                    )
                    self.errors.append(error)
                    print(f"[P0.1] ERROR: {error}", flush=True)
                    validation_passed = False
                else:
                    print(f"[P0.1] ✓ Questionnaire hash validated against expected value", flush=True)
            
            if not validation_passed:
                return False
        
        print("[P0.1] Input verification complete", flush=True)
        return True
    
    def run_boot_checks(self) -> bool:
        """
        P0.2: Boot Checks - Validate system dependencies.
        
        Runs boot-time validation checks for:
        - Python version compatibility
        - Critical package availability
        - Calibration file presence
        - spaCy model availability
        
        In PROD mode: Failures are FATAL (raises BootCheckError)
        In DEV mode: Failures log warnings but allow continuation
        
        Returns:
            True if checks passed or warnings allowed
            
        Raises:
            BootCheckError: If critical check fails in PROD mode
            
        Specification:
            P00-EN v2.0 Section 3.3
        """
        print("[P0.2] Starting boot checks", flush=True)
        
        if self.runtime_config is None:
            error = "Runtime config not available for boot checks"
            self.errors.append(error)
            raise BootCheckError("runtime_config", error, "CONFIG_MISSING")
        
        try:
            results = run_boot_checks(self.runtime_config)
            
            # Print results summary
            passed = sum(1 for v in results.values() if v)
            total = len(results)
            print(f"[P0.2] Boot checks: {passed}/{total} passed", flush=True)
            
            for check, success in results.items():
                status = "✓" if success else "✗"
                print(f"[P0.2]   {status} {check}", flush=True)
            
            return True
            
        except BootCheckError as e:
            # In PROD, this is fatal
            if self.runtime_config.mode.value == "prod":
                error = f"Boot check failed: {e}"
                self.errors.append(error)
                print(f"[P0.2] FATAL: {error}", flush=True)
                raise
            
            # In DEV, log warning and continue
            print(f"[P0.2] WARNING: {e} (continuing in {self.runtime_config.mode.value} mode)", flush=True)
            return False
    
    def initialize_determinism(self) -> bool:
        """
        P0.3: Determinism Context - Seed all RNGs.
        
        Seeds random number generators for:
        - Python random module (MANDATORY)
        - NumPy random state (MANDATORY)
        - Quantum optimizer (optional)
        - Neuromorphic controller (optional)
        - Meta-learner strategy (optional)
        
        Returns:
            True if all mandatory seeds applied successfully
            
        Postconditions:
            - self.seed_snapshot populated with seed values
            - Python random.seed() called
            - NumPy np.random.seed() called
            - Errors appended if seeding fails
            
        Specification:
            P00-EN v2.0 Section 3.4
        """
        print("[P0.3] Initializing determinism context", flush=True)
        
        seeds, status, errors = initialize_determinism_from_registry(
            self.seed_registry,
            self.policy_unit_id,
            self.correlation_id
        )
        
        if errors:
            self.errors.extend(errors)
            self._bootstrap_failed = True
            print(f"[P0.3] FATAL: Determinism initialization failed: {errors}", flush=True)
            return False
        
        # Store snapshot for validation
        self.seed_snapshot = seeds
        
        # Log seeding success
        print(f"[P0.3] Seeds applied:", flush=True)
        for component, seed_value in seeds.items():
            applied = status.get(component, False)
            marker = "✓" if applied else "○"
            print(f"[P0.3]   {marker} {component}: {seed_value}", flush=True)
        
        print("[P0.3] Determinism context initialized", flush=True)
        return True
    
    async def run_phase_zero(self) -> bool:
        """
        Execute complete Phase 0 with strict exit gate enforcement.
        
        Sequence:
            1. Check Gate 1 (Bootstrap)
            2. Execute P0.1 (Input Verification)
            3. Check Gate 2 (Input Verification)
            4. Execute P0.2 (Boot Checks)
            5. Check Gate 3 (Boot Checks)
            6. Execute P0.3 (Determinism)
            7. Check Gate 4 (Determinism)
        
        Returns:
            True if Phase 0 completed successfully (all gates passed)
            
        Exit Condition:
            self.errors == [] AND self._bootstrap_failed == False
            
        Specification:
            P00-EN v2.0 Section 4.1 - Exit Conditions & Guarantees
        """
        import asyncio

        print("\n" + "="*80, flush=True)
        print("PHASE 0: PRE-EXECUTION VALIDATION & DETERMINISTIC BOOTSTRAP", flush=True)
        print("="*80 + "\n", flush=True)
    
        # Check all gates (bootstrap already happened in __init__)
        all_passed, gate_results = check_all_gates(self)
    
        # If bootstrap failed, abort immediately
        if gate_results and not gate_results[0].passed:
            print("\n❌ Gate 1 (Bootstrap) FAILED", flush=True)
            print(get_gate_summary(gate_results), flush=True)
            return False
    
        # P0.1: Input Verification
        if not await asyncio.to_thread(self.verify_input):
            print("\n❌ P0.1 Input Verification FAILED", flush=True)
            return False
    
        # Gate 2: Input Verification
        all_passed, gate_results = check_all_gates(self)
        if not gate_results[1].passed:
            print("\n❌ Gate 2 (Input Verification) FAILED", flush=True)
            print(get_gate_summary(gate_results), flush=True)
            return False
    
        # P0.2: Boot Checks
        try:
            await asyncio.to_thread(self.run_boot_checks)
        except BootCheckError:
            print("\n❌ P0.2 Boot Checks FAILED (PROD mode)", flush=True)
            return False
    
        # Gate 3: Boot Checks
        all_passed, gate_results = check_all_gates(self)
        if not gate_results[2].passed:
            print("\n❌ Gate 3 (Boot Checks) FAILED", flush=True)
            print(get_gate_summary(gate_results), flush=True)
            return False
    
        # P0.3: Determinism
        if not await asyncio.to_thread(self.initialize_determinism):
            print("\n❌ P0.3 Determinism Initialization FAILED", flush=True)
            return False
        
        # Gate 4: Determinism (FINAL GATE)
        all_passed, gate_results = check_all_gates(self)
        if not gate_results[3].passed:
            print("\n❌ Gate 4 (Determinism) FAILED", flush=True)
            print(get_gate_summary(gate_results), flush=True)
            return False
        
        # ALL GATES PASSED
        print("\n" + "="*80, flush=True)
        print("✅ PHASE 0 COMPLETE - ALL GATES PASSED", flush=True)
        print("="*80, flush=True)
        print(get_gate_summary(gate_results), flush=True)
        print("="*80 + "\n", flush=True)
        
        return True
    
    def generate_failure_manifest(self) -> Path:
        """
        Generate failure manifest when Phase 0 fails.
        
        Returns:
            Path to verification_manifest.json
            
        Specification:
            P00-EN v2.0 Section 4.2 - Failure Manifest Generation
        """
        manifest = {
            "success": False,
            "execution_id": self.execution_id,
            "start_time": datetime.utcnow().isoformat(),
            "end_time": datetime.utcnow().isoformat(),
            "errors": self.errors,
            "phases_completed": 0,
            "phases_failed": 1,
            "artifacts_generated": [],
            "artifact_hashes": {},
            "input_pdf_path": str(self.plan_pdf_path),
            "input_pdf_sha256": self.input_pdf_sha256 or "NOT_COMPUTED",
            "questionnaire_file_path": str(self.questionnaire_path),
            "questionnaire_file_sha256": self.questionnaire_sha256 or "NOT_COMPUTED",
            "note": "Phase 0 validates file integrity only. Factory loads content after Phase 0 passes.",
        }
        
        manifest_path = self.artifacts_dir / "verification_manifest.json"
        with open(manifest_path, "w") as f:
            json.dump(manifest, f, indent=2)
        
        print(f"\nFailure manifest written to: {manifest_path}", flush=True)
        print("PIPELINE_VERIFIED=0", flush=True)
        
        return manifest_path


__all__ = ["VerifiedPipelineRunner"]
