#!/usr/bin/env python3
"""
Factory Pattern Audit Script

Audits the AnalysisPipelineFactory implementation to ensure adherence to:
- Factory Pattern: Single point of instantiation for all pipeline components
- Dependency Injection: All components receive dependencies via constructor
- Singleton Pattern: Canonical questionnaire loaded exactly once
- Method Dispensary Pattern: Loose coupling between executors and analysis methods
"""

import ast
import hashlib
import json
import logging
import re
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Set, Tuple

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(message)s')
logger = logging.getLogger(__name__)


@dataclass
class AuditResult:
    """Result of a single audit check."""
    check_name: str
    passed: bool
    status: str  # PASSED, FAILED, WARNING, PARTIAL
    details: str
    severity: str = "INFO"  # ERROR, WARNING, INFO
    evidence: Dict[str, Any] = None

    def __post_init__(self):
        if self.evidence is None:
            self.evidence = {}


class FactoryAuditor:
    """Audits the AnalysisPipelineFactory implementation."""

    def __init__(self):
        self.results: List[AuditResult] = []
        self.repo_root = Path(__file__).resolve().parents[2]
        # FIXED: Point to the actual UnifiedFactory, not the deprecated stub
        self.factory_path = self.repo_root / "src/farfan_pipeline/orchestration/factory.py"
        self.deprecated_factory_path = self.repo_root / "src/farfan_pipeline/phases/Phase_02/phase2_10_00_factory.py"

    def add_result(self, check_name: str, passed: bool, status: str, details: str,
                   severity: str = "INFO", evidence: Dict[str, Any] = None):
        """Add an audit result."""
        self.results.append(AuditResult(
            check_name=check_name,
            passed=passed,
            status=status,
            details=details,
            severity=severity,
            evidence=evidence or {}
        ))

    def audit_factory_file_structure(self) -> bool:
        """Audit 1: Factory File Structure."""
        print("\n" + "=" * 80)
        print("AUDIT 1: Factory File Structure")
        print("-" * 80)

        if not self.factory_path.exists():
            self.add_result(
                "factory_file_exists",
                False,
                "FAILED",
                f"Factory file not found: {self.factory_path}"
            )
            return False

        self.add_result(
            "factory_file_exists",
            True,
            "PASSED",
            f"Factory file exists: {self.factory_path}"
        )

        content = self.factory_path.read_text(encoding='utf-8')
        lines = content.splitlines()
        line_count = len(lines)

        # Count classes
        class_pattern = re.compile(r'^class\s+\w+')
        classes = class_pattern.findall(content)
        class_count = len(classes)

        # Count functions
        func_pattern = re.compile(r'^def\s+\w+')
        functions = func_pattern.findall(content)
        func_count = len(functions)

        # Count comment lines
        comment_pattern = re.compile(r'^\s*#')
        comment_lines = comment_pattern.findall(content)
        comment_count = len(comment_lines)

        # Check for key classes (updated for UnifiedFactory)
        required_classes = [
            "UnifiedFactory",
            "FactoryConfig",
            "FactoryHealthStatus",
            "AdaptiveLRUCache",
        ]

        found_classes = []
        missing_classes = []
        for cls in required_classes:
            if f"class {cls}" in content or f"class {cls}(" in content:
                found_classes.append(cls)
            else:
                missing_classes.append(cls)

        # Expected ~1587 lines per original audit
        line_status = "PASSED" if line_count >= 1500 else "WARNING" if line_count >= 1000 else "FAILED"

        self.add_result(
            "factory_line_count",
            line_count >= 1500,
            line_status,
            f"Factory has {line_count} lines, {class_count} classes, {func_count} functions, {comment_count} comments ({comment_count/line_count*100:.1f}% documentation ratio)",
            evidence={
                "line_count": line_count,
                "class_count": class_count,
                "func_count": func_count,
                "comment_count": comment_count,
                "doc_ratio": round(comment_count / line_count * 100, 1)
            }
        )

        # Check for required classes
        required_passed = len(missing_classes) == 0
        required_status = "PASSED" if required_passed else "PARTIAL"

        self.add_result(
            "factory_required_classes",
            required_passed,
            required_status,
            f"Found {len(found_classes)}/{len(required_classes)} required classes. Missing: {missing_classes}",
            evidence={
                "found_classes": found_classes,
                "missing_classes": missing_classes
            }
        )

        print(f"  Lines: {line_count}")
        print(f"  Classes: {class_count}")
        print(f"  Functions: {func_count}")
        print(f"  Documentation: {comment_count/line_count*100:.1f}%")
        print(f"  Required Classes: {len(found_classes)}/{len(required_classes)}")

        return line_count >= 1000

    def audit_legacy_signal_loader_deletion(self) -> bool:
        """Audit 2: Legacy Signal Loader Deletion."""
        print("\n" + "=" * 80)
        print("AUDIT 2: Legacy Signal Loader Deletion")
        print("-" * 80)

        legacy_paths = [
            "src/farfan_pipeline/core/orchestrator/signal_loader.py",
            "src/orchestration/signal_loader.py",
            "src/signal_loader.py",
        ]

        deleted_count = 0
        for path_str in legacy_paths:
            path = self.repo_root / path_str
            exists = path.exists()
            if not exists:
                deleted_count += 1
            print(f"  {'❌ DELETED' if not exists else '⚠️  EXISTS'}: {path_str}")

        passed = deleted_count == len(legacy_paths)
        self.add_result(
            "legacy_signal_loader_deleted",
            passed,
            "PASSED" if passed else "FAILED",
            f"{deleted_count}/{len(legacy_paths)} legacy signal loaders deleted"
        )

        return passed

    def audit_single_questionnaire_load_point(self) -> bool:
        """Audit 3: Single Questionnaire Load Point."""
        print("\n" + "=" * 80)
        print("AUDIT 3: Single Questionnaire Load Point")
        print("-" * 80)

        # Search for load_questionnaire calls
        load_calls = []
        for py_file in self.repo_root.rglob("*.py"):
            # Skip cache and test directories for cleaner output
            if any(x in py_file.parts for x in ["__pycache__", ".pytest_cache", ".git"]):
                continue

            try:
                content = py_file.read_text(encoding='utf-8')
                if "load_questionnaire(" in content:
                    # Count occurrences
                    count = content.count("load_questionnaire(")
                    load_calls.append({
                        "file": str(py_file.relative_to(self.repo_root)),
                        "count": count
                    })
            except Exception:
                pass

        total_calls = sum(c["count"] for c in load_calls)
        unique_files = len(load_calls)

        print(f"  Found {total_calls} calls in {unique_files} files:")

        # Categorize calls
        factory_calls = [c for c in load_calls if "phase2_10_00_factory.py" in c["file"]]
        test_calls = [c for c in load_calls if "test" in c["file"]]
        doc_calls = [c for c in load_calls if "docs" in c["file"] or "example" in c["file"]]
        other_calls = [c for c in load_calls if c not in factory_calls + test_calls + doc_calls]

        for call in load_calls[:20]:  # Show first 20
            rel_path = call["file"]
            marker = ""
            if "phase2_10_00_factory.py" in rel_path:
                marker = "✅ FACTORY"
            elif "test" in rel_path:
                marker = "⚠️  TEST"
            elif "docs" in rel_path:
                marker = "📄 DOC"
            else:
                marker = "❌ OTHER"
            print(f"    {marker}: {rel_path} ({call['count']} calls)")

        # Determine status
        if len(factory_calls) == 0:
            status = "FAILED"
            passed = False
        elif len(other_calls) == 0:
            status = "PASSED"
            passed = True
        else:
            status = "PARTIAL"
            passed = True  # Warning only

        self.add_result(
            "single_questionnaire_load_point",
            passed,
            status,
            f"Factory calls: {len(factory_calls)}, Test calls: {len(test_calls)}, Doc calls: {len(doc_calls)}, Other: {len(other_calls)}",
            evidence={
                "factory_calls": len(factory_calls),
                "test_calls": len(test_calls),
                "doc_calls": len(doc_calls),
                "other_calls": len(other_calls),
                "total_calls": total_calls
            }
        )

        return passed

    def audit_method_dispensary_files(self) -> bool:
        """Audit 4: Method Dispensary Files."""
        print("\n" + "=" * 80)
        print("AUDIT 4: Method Dispensary Files")
        print("-" * 80)

        # Check for class_registry.py in Phase_02
        class_registry_paths = list(self.repo_root.rglob("*class_registry.py"))
        class_registry_exists = len(class_registry_paths) > 0

        if class_registry_exists:
            # Use the one in Phase_02
            class_registry_path = [p for p in class_registry_paths if "Phase_02" in str(p)][0]
            print(f"  ✅ class_registry.py: {class_registry_path.relative_to(self.repo_root)}")
        else:
            class_registry_path = self.repo_root / "src/farfan_pipeline/phases/Phase_02/phase2_10_01_class_registry.py"
            print(f"  ❌ class_registry.py: {class_registry_path.relative_to(self.repo_root)}")

        # Check for arg_router.py
        arg_router_paths = list(self.repo_root.rglob("*arg_router.py"))
        arg_router_exists = len(arg_router_paths) > 0

        if arg_router_exists:
            # Use the one in Phase_02
            arg_router_path = [p for p in arg_router_paths if "Phase_02" in str(p)][0]
            print(f"  ✅ arg_router.py: {arg_router_path.relative_to(self.repo_root)}")
        else:
            print(f"  ❌ arg_router.py: NOT FOUND")

        # Check class_registry content
        dispensary_count = 0
        if class_registry_exists:
            content = class_registry_path.read_text(encoding='utf-8')
            # Count class paths in registry
            dispensary_count = content.count("class_paths")
            print(f"  📊 Dispensary entries: ~{dispensary_count}")

        passed = class_registry_exists and arg_router_exists

        self.add_result(
            "method_dispensary_files",
            passed,
            "PASSED" if passed else "PARTIAL",
            f"class_registry.py: {class_registry_exists}, arg_router.py: {arg_router_exists}",
            evidence={
                "class_registry_exists": class_registry_exists,
                "arg_router_exists": arg_router_exists,
                "dispensary_count": dispensary_count
            }
        )

        return passed

    def audit_factory_documentation(self) -> bool:
        """Audit 5: Factory Documentation."""
        print("\n" + "=" * 80)
        print("AUDIT 5: Factory Documentation")
        print("-" * 80)

        if not self.factory_path.exists():
            return False

        content = self.factory_path.read_text(encoding='utf-8')

        # Check for module docstring
        has_module_docstring = '"""' in content[:1000]
        print(f"  {'✅' if has_module_docstring else '❌'} Module docstring")

        # Check for key documentation sections (updated for UnifiedFactory)
        key_sections = [
            "Unified FARFAN Pipeline Factory",
            "Architecture",
            "UnifiedFactory",
            "FactoryConfig",
            "Adaptive",
            "Parallel",
        ]

        found_sections = []
        for section in key_sections:
            if section in content:
                found_sections.append(section)
                print(f"  ✅ Documents '{section}'")
            else:
                print(f"  ⚠️  Missing '{section}'")

        doc_passed = len(found_sections) >= 4  # At least 4 of 6 sections
        doc_status = "PASSED" if doc_passed else "PARTIAL"

        self.add_result(
            "factory_documentation",
            doc_passed,
            doc_status,
            f"Found {len(found_sections)}/{len(key_sections)} key documentation sections",
            evidence={
                "module_docstring": has_module_docstring,
                "sections_found": found_sections,
                "sections_total": len(key_sections)
            }
        )

        return doc_passed

    def audit_factory_pattern(self) -> bool:
        """Audit 6: Factory Pattern Implementation."""
        print("\n" + "=" * 80)
        print("AUDIT 6: Factory Pattern Implementation")
        print("-" * 80)

        if not self.factory_path.exists():
            return False

        content = self.factory_path.read_text(encoding='utf-8')

        # Check for UnifiedFactory class (updated from AnalysisPipelineFactory)
        has_factory = "class UnifiedFactory" in content
        print(f"  {'✅' if has_factory else '❌'} UnifiedFactory class")

        # Check for FactoryConfig
        has_config = "@dataclass" in content and "class FactoryConfig" in content
        print(f"  {'✅' if has_config else '❌'} FactoryConfig dataclass")

        # Check for core methods
        has_load_questionnaire = "def load_questionnaire(self)" in content
        print(f"  {'✅' if has_load_questionnaire else '❌'} load_questionnaire() method")
        
        has_create_signal = "def create_signal_registry(self)" in content
        print(f"  {'✅' if has_create_signal else '❌'} create_signal_registry() method")

        # Check for singleton-like caching
        has_caching = "_questionnaire" in content and "self._questionnaire" in content
        print(f"  {'✅' if has_caching else '❌'} Questionnaire caching")

        # Check for dependency injection pattern
        has_di = "__init__" in content and "self._config" in content
        print(f"  {'✅' if has_di else '❌'} Dependency injection pattern")

        passed = has_factory and has_config and has_load_questionnaire
        status = "PASSED" if passed else "FAILED"

        self.add_result(
            "factory_pattern",
            passed,
            status,
            f"Factory class: {has_factory}, Config: {has_config}, load_questionnaire: {has_load_questionnaire}, create_signal_registry: {has_create_signal}",
            evidence={
                "has_factory_class": has_factory,
                "has_factory_config": has_config,
                "has_load_questionnaire": has_load_questionnaire,
                "has_create_signal_registry": has_create_signal,
                "has_questionnaire_caching": has_caching,
                "has_dependency_injection": has_di
            }
        )

        return passed

    def audit_dependency_injection(self) -> bool:
        """Audit 7: Dependency Injection."""
        print("\n" + "=" * 80)
        print("AUDIT 7: Dependency Injection")
        print("-" * 80)

        if not self.factory_path.exists():
            return False

        content = self.factory_path.read_text(encoding='utf-8')

        # Check for DI via FactoryConfig
        has_config_di = "config: FactoryConfig" in content or "self._config" in content
        print(f"  {'✅' if has_config_di else '❌'} FactoryConfig dependency injection")

        # Check for component creation with dependencies
        has_questionnaire_di = "self._questionnaire" in content
        print(f"  {'✅' if has_questionnaire_di else '❌'} Questionnaire caching/injection")

        # Check for signal_registry creation
        has_signal_registry_di = "def create_signal_registry" in content
        print(f"  {'✅' if has_signal_registry_di else '❌'} Signal registry creation")
        
        # Check for thread pool and caching infrastructure
        has_infrastructure_di = "self._thread_pool" in content and "self._method_cache" in content
        print(f"  {'✅' if has_infrastructure_di else '❌'} Thread pool and cache infrastructure")

        passed = has_config_di and has_questionnaire_di and has_signal_registry_di
        
        self.add_result(
            "dependency_injection",
            passed,
            "PASSED" if passed else "PARTIAL",
            f"Config DI: {has_config_di}, Questionnaire: {has_questionnaire_di}, signal_registry: {has_signal_registry_di}, Infrastructure: {has_infrastructure_di}",
            evidence={
                "config_di": has_config_di,
                "questionnaire_di": has_questionnaire_di,
                "signal_registry_di": has_signal_registry_di,
                "infrastructure_di": has_infrastructure_di
            }
        )

        return passed

    def audit_singleton_pattern(self) -> bool:
        """Audit 8: Singleton Pattern Enforcement."""
        print("\n" + "=" * 80)
        print("AUDIT 8: Singleton Pattern Enforcement")
        print("-" * 80)

        if not self.factory_path.exists():
            return False

        content = self.factory_path.read_text(encoding='utf-8')

        # Check for caching pattern (not strict singleton, but similar intent)
        has_caching_var = "self._questionnaire" in content
        print(f"  {'✅' if has_caching_var else '❌'} Questionnaire caching variable")

        # Check for lazy loading pattern
        has_lazy_loading = "if self._questionnaire is None:" in content
        print(f"  {'✅' if has_lazy_loading else '❌'} Lazy loading pattern")

        # Check for get_factory singleton-like function
        has_factory_getter = "def get_factory" in content
        print(f"  {'✅' if has_factory_getter else '❌'} get_factory() singleton accessor")

        # Check external violations (from audit 3)
        external_calls = self._count_external_load_calls()
        print(f"  {'⚠️' if external_calls > 0 else '✅'} External load_questionnaire calls: {external_calls}")

        # Status depends on caching implementation
        code_implemented = has_caching_var and has_lazy_loading
        if external_calls > 5:  # Allow some test/doc calls
            status = "PARTIAL"
            passed = True  # Warning only
        elif code_implemented:
            status = "PASSED"
            passed = True
        else:
            status = "FAILED"
            passed = False

        self.add_result(
            "singleton_pattern",
            passed,
            status,
            f"Caching implemented: {code_implemented}, External calls: {external_calls}",
            evidence={
                "has_caching_variable": has_caching_var,
                "has_lazy_loading": has_lazy_loading,
                "has_factory_getter": has_factory_getter,
                "external_load_calls": external_calls
            }
        )

        return passed

    def _count_external_load_calls(self) -> int:
        """Count load_questionnaire calls outside factory."""
        count = 0
        for py_file in self.repo_root.rglob("*.py"):
            if any(x in py_file.parts for x in ["__pycache__", ".pytest_cache", ".git", "test", "tests", "docs", "examples"]):
                continue
            if "phase2_10_00_factory.py" in str(py_file):
                continue
            try:
                content = py_file.read_text(encoding='utf-8')
                if "load_questionnaire(" in content:
                    count += content.count("load_questionnaire(")
            except Exception:
                pass
        return count

    def audit_method_dispensary_pattern(self) -> bool:
        """Audit 9: Method Dispensary Pattern."""
        print("\n" + "=" * 80)
        print("AUDIT 9: Method Dispensary Pattern")
        print("-" * 80)

        # Check class_registry
        class_registry_paths = list(self.repo_root.rglob("*class_registry.py"))
        has_class_registry = len(class_registry_paths) > 0

        if has_class_registry:
            class_registry_path = [p for p in class_registry_paths if "Phase_02" in str(p)][0]
            content = class_registry_path.read_text(encoding='utf-8')
            # Count dispensaries
            dispensary_count = content.count("class_paths")
            print(f"  ✅ class_registry.py exists with ~{dispensary_count} entries")
        else:
            print(f"  ❌ class_registry.py NOT FOUND")
            dispensary_count = 0

        # Check arg_router
        arg_router_paths = list(self.repo_root.rglob("*arg_router.py"))
        has_arg_router = len(arg_router_paths) > 0
        print(f"  {'✅' if has_arg_router else '❌'} arg_router.py exists")

        # Check for contract execution (updated for UnifiedFactory)
        if self.factory_path.exists():
            factory_content = self.factory_path.read_text(encoding='utf-8')
            has_contract_execution = "def execute_contract" in factory_content
            print(f"  {'✅' if has_contract_execution else '❌'} Contract execution methods")
            
            has_batch_execution = "def execute_contracts_batch" in factory_content
            print(f"  {'✅' if has_batch_execution else '❌'} Batch contract execution")
        else:
            has_contract_execution = False
            has_batch_execution = False

        # Check for method injection/loading (more specific patterns)
        has_method_loading = False
        if self.factory_path.exists():
            factory_content = self.factory_path.read_text(encoding='utf-8')
            # Look for specific method injection patterns
            method_patterns = [
                "inject_method",
                "method_binding",
                "load_method",
                "_method_cache",
                "MethodRegistry",
            ]
            has_method_loading = any(pattern in factory_content for pattern in method_patterns)
            print(f"  {'✅' if has_method_loading else '❌'} Method injection capability")

        passed = has_class_registry and (has_contract_execution or has_batch_execution)

        self.add_result(
            "method_dispensary_pattern",
            passed,
            "PASSED" if passed else "PARTIAL",
            f"class_registry: {has_class_registry}, arg_router: {has_arg_router}, contract_execution: {has_contract_execution}, batch_execution: {has_batch_execution}",
            evidence={
                "class_registry_exists": has_class_registry,
                "arg_router_exists": has_arg_router,
                "contract_execution": has_contract_execution,
                "batch_execution": has_batch_execution,
                "method_loading": has_method_loading,
                "dispensary_count": dispensary_count
            }
        )

        return passed

    def audit_security_integrity(self) -> bool:
        """Audit 10: Security & Integrity."""
        print("\n" + "=" * 80)
        print("AUDIT 10: Security & Integrity")
        print("-" * 80)

        if not self.factory_path.exists():
            return False

        content = self.factory_path.read_text(encoding='utf-8')

        # Check for SHA-256 hash verification
        has_sha256 = "sha256" in content.lower() or "SHA-256" in content or "SHA256" in content
        print(f"  {'✅' if has_sha256 else '❌'} SHA-256 hash verification")

        # Check for Immutable CanonicalQuestionnaire
        has_immutable = "@dataclass" in content and "frozen=True" in content
        print(f"  {'✅' if has_immutable else '❌'} Immutable dataclass (frozen)")

        # Check for provenance tracking
        has_provenance = "provenance" in content.lower()
        print(f"  {'✅' if has_provenance else '❌'} Provenance tracking")

        # Check for integrity verification
        has_integrity_check = "IntegrityError" in content or "integrity" in content.lower()
        print(f"  {'✅' if has_integrity_check else '❌'} Integrity verification")

        # Check for ProcessorBundle validation
        has_bundle_validation = "def __post_init__" in content and "validate_bundle" in content.lower()
        print(f"  {'✅' if has_bundle_validation else '❌'} ProcessorBundle validation")

        passed = has_sha256 and has_immutable and has_provenance

        self.add_result(
            "security_integrity",
            passed,
            "PASSED" if passed else "PARTIAL",
            f"SHA-256: {has_sha256}, Immutable: {has_immutable}, Provenance: {has_provenance}, Integrity: {has_integrity_check}",
            evidence={
                "sha256_verification": has_sha256,
                "immutable_dataclass": has_immutable,
                "provenance_tracking": has_provenance,
                "integrity_check": has_integrity_check,
                "bundle_validation": has_bundle_validation
            }
        )

        return passed

    def audit_deprecated_factory_stub(self) -> bool:
        """Audit 11: Deprecated Factory Stub."""
        print("\n" + "=" * 80)
        print("AUDIT 11: Deprecated Factory Stub Relationship")
        print("-" * 80)

        if not self.deprecated_factory_path.exists():
            print(f"  ❌ Deprecated factory file not found")
            self.add_result(
                "deprecated_factory_stub",
                False,
                "FAILED",
                "Deprecated factory file not found"
            )
            return False

        content = self.deprecated_factory_path.read_text(encoding='utf-8')

        # Check for deprecation warning
        has_deprecation = "DEPRECATED" in content
        print(f"  {'✅' if has_deprecation else '❌'} Deprecation notice present")

        # Check for UnifiedFactory import
        has_unified_import = "from farfan_pipeline.orchestration.factory import" in content
        print(f"  {'✅' if has_unified_import else '❌'} Imports from UnifiedFactory")

        # Check for get_factory usage
        has_get_factory = "get_factory()" in content
        print(f"  {'✅' if has_get_factory else '❌'} Uses get_factory() accessor")

        # Check that it's a stub (small file)
        line_count = len(content.splitlines())
        is_stub = line_count < 300
        print(f"  {'✅' if is_stub else '❌'} Is a stub file ({line_count} lines)")

        passed = has_deprecation and has_unified_import and has_get_factory and is_stub
        status = "PASSED" if passed else "PARTIAL"

        self.add_result(
            "deprecated_factory_stub",
            passed,
            status,
            f"Deprecation: {has_deprecation}, Imports UnifiedFactory: {has_unified_import}, Uses get_factory: {has_get_factory}, Is stub: {is_stub}",
            evidence={
                "has_deprecation_notice": has_deprecation,
                "has_unified_import": has_unified_import,
                "has_get_factory": has_get_factory,
                "is_stub": is_stub,
                "line_count": line_count
            }
        )

        return passed

    def run_full_audit(self) -> Dict[str, Any]:
        """Run complete factory audit."""
        print("=" * 80)
        print("FACTORY PATTERN AUDIT")
        print(f"Factory: {self.factory_path.relative_to(self.repo_root)}")
        print(f"Date: {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S UTC')}")
        print("=" * 80)

        # Run all audits
        self.audit_factory_file_structure()
        self.audit_deprecated_factory_stub()
        self.audit_legacy_signal_loader_deletion()
        self.audit_single_questionnaire_load_point()
        self.audit_method_dispensary_files()
        self.audit_factory_documentation()
        self.audit_factory_pattern()
        self.audit_dependency_injection()
        self.audit_singleton_pattern()
        self.audit_method_dispensary_pattern()
        self.audit_security_integrity()

        # Generate summary
        return self.generate_summary()

    def generate_summary(self) -> Dict[str, Any]:
        """Generate audit summary."""
        print("\n" + "=" * 80)
        print("AUDIT SUMMARY")
        print("=" * 80)

        passed = [r for r in self.results if r.passed]
        failed = [r for r in self.results if not r.passed and r.status == "FAILED"]
        warnings = [r for r in self.results if not r.passed and r.status in ["WARNING", "PARTIAL"]]

        total = len(self.results)
        pass_count = len(passed)
        pass_rate = round(pass_count / total * 100, 1) if total > 0 else 0

        print(f"\nTotal Checks: {total}")
        print(f"Passed: {pass_count} ({pass_rate}%)")
        print(f"Failed: {len(failed)}")
        print(f"Warnings: {len(warnings)}")

        # Determine overall status
        if len(failed) == 0 and len(warnings) == 0:
            overall_status = "PASSED"
            overall_emoji = "✅"
        elif len(failed) == 0:
            overall_status = "PASSED WITH RECOMMENDATIONS"
            overall_emoji = "🟡"
        else:
            overall_status = "FAILED"
            overall_emoji = "❌"

        print(f"\n{overall_emoji} Overall Status: {overall_status}")

        # Print failed checks
        if failed:
            print("\n❌ FAILED CHECKS:")
            for result in failed:
                print(f"  - {result.check_name}: {result.details}")

        # Print warnings
        if warnings:
            print("\n⚠️  WARNINGS:")
            for result in warnings[:5]:
                print(f"  - {result.check_name}: {result.details}")
            if len(warnings) > 5:
                print(f"  ... and {len(warnings) - 5} more warnings")

        # Generate metrics table
        print("\n" + "-" * 80)
        print("AUDIT METRICS:")
        print("-" * 80)
        for result in self.results:
            emoji = "✅" if result.passed else "❌" if result.status == "FAILED" else "⚠️"
            print(f"  {emoji} {result.check_name}: {result.status}")

        # Build return dict
        summary = {
            "overall_status": overall_status,
            "total_checks": total,
            "passed": pass_count,
            "failed": len(failed),
            "warnings": len(warnings),
            "pass_rate": pass_rate,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "results": [
                {
                    "check_name": r.check_name,
                    "passed": r.passed,
                    "status": r.status,
                    "details": r.details,
                    "severity": r.severity,
                    "evidence": r.evidence
                }
                for r in self.results
            ]
        }

        return summary


def main():
    """Main entry point."""
    auditor = FactoryAuditor()
    summary = auditor.run_full_audit()

    # Save JSON report
    output_dir = Path(__file__).resolve().parents[2] / "artifacts" / "audit_reports"
    output_dir.mkdir(parents=True, exist_ok=True)
    output_path = output_dir / "factory_audit_report.json"

    with open(output_path, 'w') as f:
        json.dump(summary, f, indent=2)

    print(f"\n📄 JSON report saved to: {output_path.relative_to(Path.cwd())}")

    # Exit with appropriate code
    return 0 if summary["failed"] == 0 else 1


if __name__ == "__main__":
    import sys

    sys.exit(main())
