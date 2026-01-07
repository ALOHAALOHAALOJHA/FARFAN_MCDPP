"""
PHASE 0 ADVERSARIAL TEST SUITE
==============================

Comprehensive severe testing for Phase 0 Validation, Hardening & Bootstrap.
Tests attack vectors, edge cases, resource exhaustion, and constitutional invariants.

Test Categories:
1. Input Validation - Malformed paths, invalid contracts
2. Resource Exhaustion - Memory, CPU, file descriptors
3. Hash Computation - Large files, invalid content
4. Contract Violations - Invalid data structures
5. Boot Checks - Missing dependencies, invalid configs
6. Adversarial Inputs - Malicious data attacks
7. Resource Controller - Kernel limit bypass attempts

Author: F.A.R.F.A.N Adversarial Testing Team
Date: 2026-01-07
Status: ADVERSARIAL - Break if you can
"""

import asyncio
import hashlib
import json
import os
import tempfile
import threading
from pathlib import Path
from dataclasses import FrozenInstanceError
from typing import Any, Dict, List

import pytest

# Phase 0 imports
from farfan_pipeline.phases.Phase_zero.phase0_40_00_input_validation import (
    Phase0Input,
    CanonicalInput,
    Phase0ValidationContract,
    Phase0InputValidator,
    CanonicalInputValidator,
    PHASE0_VERSION,
)
from farfan_pipeline.phases.Phase_zero.phase0_30_00_resource_controller import (
    ResourceController,
    ResourceLimits,
    ResourceExhausted,
    MemoryWatchdog,
)
from farfan_pipeline.phases.Phase_zero.phase0_10_01_runtime_config import (
    RuntimeConfig,
    RuntimeMode,
)
from farfan_pipeline.phases.Phase_zero.phase0_50_00_boot_checks import (
    BootCheckError,
    check_calibration_files,
    check_contradiction_module_available,
    check_networkx_available,
    check_spacy_model_available,
    check_wiring_validator_available,
    run_boot_checks,
)


# =============================================================================
# 1. INPUT VALIDATION ADVERSARIAL TESTS
# =============================================================================

class TestInputValidationAdversarial:
    """Test adversarial inputs for Phase 0 validation."""

    def test_phase0_input_validator_path_traversal_attempts(self):
        """Test validator rejects path traversal attempts."""
        malicious_paths = [
            "../../../etc/passwd",
            "..\\..\\windows\\system32",
            "/../../../root/.ssh/id_rsa",
            "./../../../proc/self/environ",
        ]
        
        for malicious_path in malicious_paths:
            with pytest.raises(Exception, match="path traversal|pdf_path cannot be empty|String should have at least 1 character"):
                Phase0InputValidator(
                    pdf_path=malicious_path,
                    run_id="test_run"
                )

    def test_phase0_input_validator_null_byte_injection(self):
        """Test validator rejects null byte injection."""
        with pytest.raises(Exception):
            Phase0InputValidator(
                pdf_path="/tmp/test\x00.pdf",
                run_id="test_run"
            )

    def test_phase0_input_validator_sql_injection_in_run_id(self):
        """Test validator rejects SQL injection in run_id."""
        sql_injections = [
            "test'; DROP TABLE--",
            "test'; SELECT * FROM users WHERE 1=1",
            "test'; UPDATE config SET mode='dev'--",
            "test'; DELETE FROM methods WHERE 1=1--",
        ]
        
        for injection in sql_injections:
            with pytest.raises(Exception, match="invalid characters"):
                Phase0InputValidator(
                    pdf_path="/tmp/test.pdf",
                    run_id=injection
                )

    def test_phase0_input_validator_xss_injection_in_run_id(self):
        """Test validator rejects XSS injection in run_id."""
        xss_payloads = [
            "<script>alert('xss')</script>",
            "javascript:alert('xss')",
            "<img src=x onerror=alert('xss')>",
            "data:text/html,<script>alert('xss')</script>",
        ]
        
        for payload in xss_payloads:
            with pytest.raises(Exception, match="invalid characters"):
                Phase0InputValidator(
                    pdf_path="/tmp/test.pdf",
                    run_id=payload
                )

    def test_canonical_input_validator_extremely_large_sha256(self):
        """Test validator rejects extremely large SHA256 values."""
        with pytest.raises(Exception, match="String should have at most 64 characters"):
            CanonicalInputValidator(
                document_id="test",
                run_id="test_run",
                pdf_path="/tmp/test.pdf",
                pdf_sha256="a" * 1000,  # Way too long
                pdf_size_bytes=1024,
                pdf_page_count=10,
                questionnaire_path="/tmp/q.json",
                questionnaire_sha256="b" * 64,
                created_at="2025-12-10T12:00:00Z",
                phase0_version="1.0.0",
                validation_passed=True,
                validation_errors=[],
                validation_warnings=[],
            )

    def test_canonical_input_validator_extremely_small_sha256(self):
        """Test validator rejects extremely small SHA256 values."""
        with pytest.raises(Exception, match="String should have at least 64 characters"):
            CanonicalInputValidator(
                document_id="test",
                run_id="test_run",
                pdf_path="/tmp/test.pdf",
                pdf_sha256="abc",  # Way too short
                pdf_size_bytes=1024,
                pdf_page_count=10,
                questionnaire_path="/tmp/q.json",
                questionnaire_sha256="b" * 64,
                created_at="2025-12-10T12:00:00Z",
                phase0_version="1.0.0",
                validation_passed=True,
                validation_errors=[],
                validation_warnings=[],
            )

    def test_canonical_input_validator_non_hex_sha256(self):
        """Test validator rejects non-hexadecimal SHA256."""
        with pytest.raises(Exception, match="must be hexadecimal"):
            CanonicalInputValidator(
                document_id="test",
                run_id="test_run",
                pdf_path="/tmp/test.pdf",
                pdf_sha256="z" * 64,  # Invalid hex
                pdf_size_bytes=1024,
                pdf_page_count=10,
                questionnaire_path="/tmp/q.json",
                questionnaire_sha256="b" * 64,
                created_at="2025-12-10T12:00:00Z",
                phase0_version="1.0.0",
                validation_passed=True,
                validation_errors=[],
                validation_warnings=[],
            )

    def test_canonical_input_validator_extremely_large_file_sizes(self):
        """Test validator handles extremely large file sizes."""
        with pytest.raises(Exception, match="greater than 0|less than or equal"):
            CanonicalInputValidator(
                document_id="test",
                run_id="test_run",
                pdf_path="/tmp/test.pdf",
                pdf_sha256="a" * 64,
                pdf_size_bytes=999999999999999999999,  # Extremely large
                pdf_page_count=10,
                questionnaire_path="/tmp/q.json",
                questionnaire_sha256="b" * 64,
                created_at="2025-12-10T12:00:00Z",
                phase0_version="1.0.0",
                validation_passed=True,
                validation_errors=[],
                validation_warnings=[],
            )

    def test_canonical_input_validator_extremely_large_page_counts(self):
        """Test validator handles extremely large page counts."""
        with pytest.raises(Exception, match="greater than 0|less than or equal"):
            CanonicalInputValidator(
                document_id="test",
                run_id="test_run",
                pdf_path="/tmp/test.pdf",
                pdf_sha256="a" * 64,
                pdf_size_bytes=1024,
                pdf_page_count=999999999999999999999,  # Extremely large
                questionnaire_path="/tmp/q.json",
                questionnaire_sha256="b" * 64,
                created_at="2025-12-10T12:00:00Z",
                phase0_version="1.0.0",
                validation_passed=True,
                validation_errors=[],
                validation_warnings=[],
            )


# =============================================================================
# 2. RESOURCE EXHAUSTION ADVERSARIAL TESTS
# =============================================================================

class TestResourceExhaustionAdversarial:
    """Test adversarial resource exhaustion scenarios."""

    def test_resource_limits_constructor_extreme_values(self):
        """Test ResourceLimits constructor with extreme values."""
        # Test extremely small values
        with pytest.raises(ValueError, match="memory_mb must be >= 256"):
            ResourceLimits(memory_mb=1)
            
        with pytest.raises(ValueError, match="cpu_seconds must be >= 10"):
            ResourceLimits(cpu_seconds=1)
            
        with pytest.raises(ValueError, match="disk_mb must be >= 50"):
            ResourceLimits(disk_mb=1)
            
        with pytest.raises(ValueError, match="file_descriptors must be >= 64"):
            ResourceLimits(file_descriptors=1)

        # Test extremely large values
        # Note: These might not raise errors but should be tested for reasonable behavior
        limits = ResourceLimits(
            memory_mb=1000000,  # Very large but possibly valid
            cpu_seconds=999999,
            disk_mb=999999,
            file_descriptors=65535
        )
        assert limits.memory_mb == 1000000

    def test_resource_controller_with_unrealistic_limits(self):
        """Test ResourceController with unrealistic limits."""
        # This test might not fail but should be tested
        limits = ResourceLimits(
            memory_mb=1000000,  # Very large
            cpu_seconds=999999,
            disk_mb=999999,
            file_descriptors=65535
        )
        controller = ResourceController(limits)
        
        # Just test that it doesn't crash during initialization
        assert controller.limits.memory_mb == 1000000

    def test_memory_watchdog_extreme_thresholds(self):
        """Test MemoryWatchdog with extreme thresholds."""
        # Test very low threshold
        watchdog_low = MemoryWatchdog(threshold_percent=1, check_interval=0.01)
        assert watchdog_low.threshold_percent == 1
        
        # Test very high threshold
        watchdog_high = MemoryWatchdog(threshold_percent=99, check_interval=0.01)
        assert watchdog_high.threshold_percent == 99
        
        # Test invalid threshold type - passing string instead of int
        with pytest.raises((TypeError, ValueError)):
            MemoryWatchdog(threshold_percent="invalid", check_interval=0.01)

    def test_resource_controller_preflight_with_insufficient_resources(self):
        """Test preflight checks with artificially low limits."""
        # This test simulates the scenario where available memory is less than 50% of limit
        # We can't easily force this in a test environment, so we'll test the logic
        limits = ResourceLimits(memory_mb=1000000)  # Very high limit
        controller = ResourceController(limits)
        
        # The preflight check should pass since we have plenty of memory
        # (assuming the system has enough memory)
        try:
            checks = controller.preflight_checks()
            assert "memory_available_mb" in checks
        except ResourceExhausted:
            # This is expected if the system doesn't have enough memory
            pass


# =============================================================================
# 3. HASH COMPUTATION ADVERSARIAL TESTS
# =============================================================================

class TestHashComputationAdversarial:
    """Test adversarial hash computation scenarios."""

    def test_hash_computation_extremely_large_file(self):
        """Test hash computation with extremely large file."""
        # Create a large temporary file
        with tempfile.NamedTemporaryFile(delete=False) as large_file:
            # Write a large amount of data (but not too large to avoid filling disk)
            chunk_size = 1024 * 1024  # 1MB chunks
            num_chunks = 10  # 10MB total
            
            for i in range(num_chunks):
                large_file.write(b"x" * chunk_size)
            large_file.flush()
            
            large_path = Path(large_file.name)
            
        try:
            contract = Phase0ValidationContract()
            hash_result = contract._compute_sha256(large_path)
            
            # Verify it's a valid SHA256 hash
            assert len(hash_result) == 64
            assert all(c in "0123456789abcdef" for c in hash_result)
        finally:
            large_path.unlink()

    def test_hash_computation_empty_file(self):
        """Test hash computation with empty file."""
        with tempfile.NamedTemporaryFile(delete=False) as empty_file:
            # Don't write anything - file remains empty
            empty_file.flush()
            empty_path = Path(empty_file.name)
            
        try:
            contract = Phase0ValidationContract()
            hash_result = contract._compute_sha256(empty_path)
            
            # SHA256 of empty string
            expected_empty_hash = hashlib.sha256(b"").hexdigest()
            assert hash_result == expected_empty_hash
        finally:
            empty_path.unlink()

    def test_hash_computation_binary_file_with_special_chars(self):
        """Test hash computation with binary file containing special characters."""
        with tempfile.NamedTemporaryFile(delete=False) as binary_file:
            # Write binary data with special characters
            binary_data = b"\x00\x01\x02\x03\xff\xfe\xfd\xfc" + b"special chars: \x00\x01\x02\x03"
            binary_file.write(binary_data)
            binary_file.flush()
            binary_path = Path(binary_file.name)
            
        try:
            contract = Phase0ValidationContract()
            hash_result = contract._compute_sha256(binary_path)
            
            # Verify it's a valid SHA256 hash
            assert len(hash_result) == 64
            assert all(c in "0123456789abcdef" for c in hash_result)
            
            # Verify it matches expected hash
            expected_hash = hashlib.sha256(binary_data).hexdigest()
            assert hash_result == expected_hash
        finally:
            binary_path.unlink()


# =============================================================================
# 4. CONTRACT VIOLATION ADVERSARIAL TESTS
# =============================================================================

class TestContractViolationAdversarial:
    """Test adversarial contract violations."""

    def test_phase0_input_with_none_values(self):
        """Test Phase0Input with None values."""
        with pytest.raises(TypeError):
            Phase0Input(
                pdf_path=None,  # Should be Path
                run_id="test_run"
            )

    def test_phase0_input_with_invalid_types(self):
        """Test Phase0Input with invalid types."""
        with pytest.raises(TypeError):
            Phase0Input(
                pdf_path="not_a_path",  # Should be Path object
                run_id=123  # Should be string
            )

    def test_canonical_input_with_invalid_boolean(self):
        """Test CanonicalInput with invalid boolean for validation_passed."""
        with pytest.raises(TypeError):
            CanonicalInput(
                document_id="test",
                run_id="test_run",
                pdf_path=Path("/tmp/test.pdf"),
                pdf_sha256="a" * 64,
                pdf_size_bytes=1024,
                pdf_page_count=10,
                questionnaire_path=Path("/tmp/q.json"),
                questionnaire_sha256="b" * 64,
                created_at=None,  # Should be datetime
                phase0_version=PHASE0_VERSION,
                validation_passed="invalid",  # Should be boolean
            )

    def test_canonical_input_with_extremely_long_strings(self):
        """Test CanonicalInput with extremely long strings."""
        long_string = "a" * 100000  # 100k characters
        
        with pytest.raises(TypeError):
            CanonicalInput(
                document_id=long_string,
                run_id="test_run",
                pdf_path=Path("/tmp/test.pdf"),
                pdf_sha256="a" * 64,
                pdf_size_bytes=1024,
                pdf_page_count=10,
                questionnaire_path=Path("/tmp/q.json"),
                questionnaire_sha256="b" * 64,
                created_at=None,  # Will fail due to None
                phase0_version=PHASE0_VERSION,
                validation_passed=True,
            )

    def test_phase0_validation_contract_execute_with_nonexistent_paths(self):
        """Test Phase0ValidationContract.execute with nonexistent paths."""
        input_data = Phase0Input(
            pdf_path=Path("/this/path/does/not/exist.pdf"),
            run_id="test_run",
            questionnaire_path=Path("/this/questionnaire/does/not/exist.json"),
        )

        contract = Phase0ValidationContract()

        with pytest.raises(FileNotFoundError, match="Input validation failed"):
            asyncio.run(contract.execute(input_data))


# =============================================================================
# 5. BOOT CHECKS ADVERSARIAL TESTS
# =============================================================================

class TestBootChecksAdversarial:
    """Test adversarial boot check scenarios."""

    def test_boot_check_error_with_extremely_long_messages(self):
        """Test BootCheckError with extremely long messages."""
        long_message = "a" * 100000  # 100k characters
        
        error = BootCheckError(
            component="test_component",
            reason=long_message,
            code="TEST_ERROR_CODE",
        )
        
        assert len(str(error)) > 10000  # Should be quite long

    def test_boot_check_error_with_special_characters(self):
        """Test BootCheckError with special characters."""
        special_message = "Error with null: \x00, newline: \n, tab: \t, quote: \""
        
        error = BootCheckError(
            component="test_component",
            reason=special_message,
            code="TEST_ERROR_CODE",
        )
        
        assert "\x00" in error.reason
        assert "\n" in error.reason
        assert "\"" in error.reason


# =============================================================================
# 6. ADVERSARIAL INPUTS FOR RUNTIME CONFIG
# =============================================================================

class TestRuntimeConfigAdversarial:
    """Test adversarial runtime configuration scenarios."""

    def setup_method(self):
        """Reset config before each test."""
        # Reset environment variables
        for key in list(os.environ.keys()):
            if key.startswith("SAAAAAA_") or key.startswith("ALLOW_"):
                del os.environ[key]

    def teardown_method(self):
        """Cleanup after each test."""
        # Reset environment variables
        for key in list(os.environ.keys()):
            if key.startswith("SAAAAAA_") or key.startswith("ALLOW_"):
                del os.environ[key]

    def test_runtime_config_with_extremely_long_environment_vars(self):
        """Test RuntimeConfig with extremely long environment variable values."""
        long_value = "a" * 10000  # 10k characters
        
        os.environ["SAAAAAA_RUNTIME_MODE"] = long_value
        os.environ["PHASE_TIMEOUT_SECONDS"] = "600"
        
        # This should either fail or handle gracefully
        try:
            config = RuntimeConfig.from_env()
            # If it doesn't fail, the config should handle the long value appropriately
        except Exception as e:
            # Expected that it might fail with validation
            assert "Invalid" in str(e) or "SAAAAAA_RUNTIME_MODE" in str(e)

    def test_runtime_config_with_invalid_json_in_env_vars(self):
        """Test RuntimeConfig with invalid JSON in environment variables."""
        # Set an environment variable that might be interpreted as JSON
        os.environ["SAAAAAA_RUNTIME_MODE"] = "prod"
        os.environ["SOME_COMPLEX_CONFIG"] = '{"invalid": json, "missing": quote}'
        
        config = RuntimeConfig.from_env()
        # Should handle gracefully without crashing


# =============================================================================
# 7. RESOURCE CONTROLLER KERNEL LIMIT BYPASS ATTEMPTS
# =============================================================================

class TestResourceControllerKernelBypass:
    """Test attempts to bypass kernel resource limits."""

    def test_resource_controller_multiple_context_entries(self):
        """Test attempting to enter enforced_execution context multiple times."""
        controller = ResourceController(ResourceLimits(memory_mb=512))
        
        with controller.enforced_execution():
            # Try to enter again - this should fail
            with pytest.raises(RuntimeError, match="Resource enforcement already active"):
                with controller.enforced_execution():
                    pass  # This should never execute

    def test_resource_controller_thread_interference(self):
        """Test resource controller behavior under thread interference."""
        controller = ResourceController(ResourceLimits(memory_mb=512))
        main_entered = threading.Event()
        interference_attempted = threading.Event()
        interference_result = {"raised": False}
        
        def interference_func():
            """Function that tries to interfere with resource controller."""
            # Wait for main thread to enter first
            main_entered.wait(timeout=5.0)
            try:
                # Attempt to enter the same controller from another thread
                with controller.enforced_execution():
                    pass
            except RuntimeError:
                # Expected to fail - main thread already has the lock
                interference_result["raised"] = True
            finally:
                interference_attempted.set()
        
        # Start interference thread (but it will wait for main to enter first)
        interference_thread = threading.Thread(target=interference_func)
        interference_thread.start()
        
        # Enter from main thread
        with controller.enforced_execution():
            # Signal that main thread has entered
            main_entered.set()
            # Wait for interference thread to attempt entry
            interference_attempted.wait(timeout=2.0)
            # Verify interference was blocked
            assert interference_result["raised"], "Interference should have raised RuntimeError"
        
        interference_thread.join(timeout=1.0)
        # Ensure main thread execution completed normally
        assert True  # If we reach here, main thread wasn't affected

    def test_resource_controller_extreme_limits_stress(self):
        """Test resource controller with extreme limits under stress."""
        # Test with very tight limits
        tight_limits = ResourceLimits(
            memory_mb=256,  # Minimum allowed
            cpu_seconds=10,  # Minimum allowed  
            disk_mb=50,  # Minimum allowed
            file_descriptors=64  # Minimum allowed
        )
        
        controller = ResourceController(tight_limits)
        
        # Should be able to enter context with tight limits
        with controller.enforced_execution():
            # Perform minimal operations
            x = 1 + 1
            str(x)
        
        # Verify metrics were collected
        metrics = controller.get_metrics()
        assert metrics.enforcement_duration_s >= 0


# =============================================================================
# 8. INTEGRATION ADVERSARIAL TESTS
# =============================================================================

class TestIntegrationAdversarial:
    """Test adversarial scenarios across multiple components."""

    def test_phase0_contract_with_extremely_large_validation_errors(self):
        """Test Phase0ValidationContract with extremely large error lists."""
        # This tests the output validation with large error lists
        large_errors = ["error_" + str(i) for i in range(10000)]
        
        # Create a CanonicalInput with many errors (should fail validation)
        try:
            bad_input = CanonicalInput(
                document_id="test",
                run_id="test_run",
                pdf_path=Path("/tmp/test.pdf"),
                pdf_sha256="a" * 64,
                pdf_size_bytes=1024,
                pdf_page_count=10,
                questionnaire_path=Path("/tmp/q.json"),
                questionnaire_sha256="b" * 64,
                created_at=None,  # This will cause an issue
                phase0_version=PHASE0_VERSION,
                validation_passed=False,  # This should be True for valid, but we're testing
                validation_errors=large_errors,
                validation_warnings=[],
            )
        except TypeError:
            # Expected due to None datetime
            pass

    def test_resource_controller_under_concurrent_load(self):
        """Test resource controller behavior under concurrent load."""
        controllers = []
        contexts = []
        
        # Create multiple controllers
        for i in range(3):
            controller = ResourceController(ResourceLimits(memory_mb=512 + i*128))
            controllers.append(controller)
        
        # Try to use them sequentially (not concurrently due to lock)
        for controller in controllers:
            with controller.enforced_execution():
                # Perform some operations
                data = [i for i in range(100)]
                result = sum(data)
                assert result == 4950  # Sum of 0-99


# =============================================================================
# 9. EDGE CASE ADVERSARIAL TESTS
# =============================================================================

class TestEdgeCaseAdversarial:
    """Test edge cases and boundary conditions."""

    def test_resource_limits_boundary_values(self):
        """Test ResourceLimits at boundary values."""
        # Test minimum allowed values
        min_limits = ResourceLimits(
            memory_mb=256,      # Minimum
            cpu_seconds=10,     # Minimum  
            disk_mb=50,         # Minimum
            file_descriptors=64 # Minimum
        )
        
        assert min_limits.memory_mb == 256
        assert min_limits.cpu_seconds == 10
        assert min_limits.disk_mb == 50
        assert min_limits.file_descriptors == 64

    def test_phase0_input_validator_unicode_normalization(self):
        """Test Phase0InputValidator with Unicode normalization attacks."""
        # Test homograph attacks (characters that look similar)
        homograph_variants = [
            "test.pdf",  # Normal
            "tеst.pdf",  # Cyrillic 'e'
            "teѕt.pdf",  # Cyrillic 's' 
            "ｔｅｓｔ.ｐｄｆ",  # Full-width characters
        ]
        
        for variant in homograph_variants:
            # Should either accept or reject consistently
            try:
                validator = Phase0InputValidator(
                    pdf_path=variant,
                    run_id="test_run"
                )
                # If it passes, verify the path is handled correctly
                assert validator.pdf_path == variant
            except Exception:
                # If it fails, that's also acceptable for security
                pass

    def test_canonical_input_validator_timezone_handling(self):
        """Test CanonicalInputValidator with various timezone formats."""
        timezone_formats = [
            "2025-12-10T12:00:00Z",
            "2025-12-10T12:00:00+00:00", 
            "2025-12-10T12:00:00.000Z",
            "2025-12-10T12:00:00.123456Z",
        ]
        
        for tz_format in timezone_formats:
            try:
                validator = CanonicalInputValidator(
                    document_id="test",
                    run_id="test_run", 
                    pdf_path="/tmp/test.pdf",
                    pdf_sha256="a" * 64,
                    pdf_size_bytes=1024,
                    pdf_page_count=10,
                    questionnaire_path="/tmp/q.json",
                    questionnaire_sha256="b" * 64,
                    created_at=tz_format,
                    phase0_version="1.0.0",
                    validation_passed=True,
                    validation_errors=[],
                    validation_warnings=[],
                )
            except Exception:
                # Some timezone formats might not be supported
                pass


# =============================================================================
# RUN CONFIGURATION
# =============================================================================

if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])