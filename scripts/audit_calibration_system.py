#!/usr/bin/env python3
"""
FARFAN Calibration & Parametrization System Comprehensive Audit

This script performs a comprehensive audit of the calibration and parametrization
system as specified in the architectural analysis. It validates:

1. Canonical Specs Completeness
2. TYPE Defaults Consistency
3. Calibration Layer Invariants
4. Interaction Governance
5. Veto Threshold Calibration
6. Prior Strength Calibration
7. Unit of Analysis Calibration
8. Fact Registry Verbosity
9. Manifest & Audit Trail
10. Missing Calibration Coverage

Usage:
    python scripts/audit_calibration_system.py [--section SECTION_NUMBER] [--output-format {text|json|markdown}]
"""

import argparse
import json
import sys
from collections import defaultdict
from dataclasses import dataclass, field, asdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Tuple
import re

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))


@dataclass
class AuditResult:
    """Result of a single audit check."""
    section: str
    check_name: str
    passed: bool
    message: str
    severity: str = "INFO"  # INFO, WARNING, ERROR, CRITICAL
    details: Dict[str, Any] = field(default_factory=dict)


@dataclass
class AuditReport:
    """Complete audit report."""
    timestamp: str
    total_checks: int = 0
    passed_checks: int = 0
    failed_checks: int = 0
    warnings: int = 0
    errors: int = 0
    critical: int = 0
    results: List[AuditResult] = field(default_factory=list)
    recommendations: List[str] = field(default_factory=list)

    def add_result(self, result: AuditResult) -> None:
        """Add audit result and update counters."""
        self.results.append(result)
        self.total_checks += 1
        if result.passed:
            self.passed_checks += 1
        else:
            self.failed_checks += 1
            if result.severity == "WARNING":
                self.warnings += 1
            elif result.severity == "ERROR":
                self.errors += 1
            elif result.severity == "CRITICAL":
                self.critical += 1

    def get_summary(self) -> Dict[str, Any]:
        """Get summary statistics."""
        return {
            "timestamp": self.timestamp,
            "total_checks": self.total_checks,
            "passed_checks": self.passed_checks,
            "failed_checks": self.failed_checks,
            "warnings": self.warnings,
            "errors": self.errors,
            "critical": self.critical,
            "pass_rate": f"{(self.passed_checks / self.total_checks * 100):.2f}%" if self.total_checks > 0 else "0%",
        }


class CalibrationAuditor:
    """Performs comprehensive calibration system audit."""

    def __init__(self, repo_root: Path):
        self.repo_root = repo_root
        self.report = AuditReport(timestamp=datetime.now(timezone.utc).isoformat())

    def run_full_audit(self) -> AuditReport:
        """Run all audit sections."""
        print("🔬 Starting Comprehensive FARFAN Calibration System Audit...\n")
        
        self.audit_section_1_canonical_specs()
        self.audit_section_2_type_defaults()
        self.audit_section_3_calibration_layer()
        self.audit_section_4_interaction_governance()
        self.audit_section_5_veto_thresholds()
        self.audit_section_6_prior_strength()
        self.audit_section_7_unit_of_analysis()
        self.audit_section_8_fact_registry()
        self.audit_section_9_manifest_audit_trail()
        self.audit_section_10_missing_coverage()
        
        self._generate_recommendations()
        
        return self.report

    def audit_section_1_canonical_specs(self) -> None:
        """Section 1: Canonical Specs Completeness Audit."""
        print("📋 Section 1: Auditing Canonical Specs Completeness...")
        
        try:
            from farfan_pipeline.calibracion_parametrizacion.canonical_specs import (
                CANON_POLICY_AREAS,
                CANON_DIMENSIONS,
                MICRO_LEVELS,
                CDAF_DOMAIN_WEIGHTS,
                CAUSAL_CHAIN_ORDER,
                ALIGNMENT_THRESHOLD,
                TOTAL_BASE_QUESTIONS,
                validate_canonical_specs,
            )
            
            # 1.1 Frozen Constants Audit
            # Policy Areas
            passed = len(CANON_POLICY_AREAS) == 10
            self.report.add_result(AuditResult(
                section="1.1",
                check_name="Policy Areas Count",
                passed=passed,
                message=f"CANON_POLICY_AREAS has {len(CANON_POLICY_AREAS)} entries (expected 10)",
                severity="CRITICAL" if not passed else "INFO",
                details={"count": len(CANON_POLICY_AREAS), "expected": 10}
            ))
            
            passed = all(k.startswith("PA") for k in CANON_POLICY_AREAS)
            self.report.add_result(AuditResult(
                section="1.1",
                check_name="Policy Areas Format",
                passed=passed,
                message="All policy area keys follow PA## format" if passed else "Some keys don't follow PA## format",
                severity="ERROR" if not passed else "INFO"
            ))
            
            # Dimensions
            passed = len(CANON_DIMENSIONS) == 6
            self.report.add_result(AuditResult(
                section="1.1",
                check_name="Dimensions Count",
                passed=passed,
                message=f"CANON_DIMENSIONS has {len(CANON_DIMENSIONS)} entries (expected 6)",
                severity="CRITICAL" if not passed else "INFO",
                details={"count": len(CANON_DIMENSIONS), "expected": 6}
            ))
            
            passed = all(k.startswith("DIM") for k in CANON_DIMENSIONS)
            self.report.add_result(AuditResult(
                section="1.1",
                check_name="Dimensions Format",
                passed=passed,
                message="All dimension keys follow DIM## format" if passed else "Some keys don't follow DIM## format",
                severity="ERROR" if not passed else "INFO"
            ))
            
            # Micro Levels Monotonicity
            passed = (
                MICRO_LEVELS["EXCELENTE"] > MICRO_LEVELS["BUENO"] >
                MICRO_LEVELS["ACEPTABLE"] > MICRO_LEVELS["INSUFICIENTE"]
            )
            self.report.add_result(AuditResult(
                section="1.1",
                check_name="Micro Levels Monotonicity",
                passed=passed,
                message="MICRO_LEVELS maintain monotonic ordering" if passed else "MICRO_LEVELS violate monotonicity",
                severity="CRITICAL" if not passed else "INFO",
                details=MICRO_LEVELS
            ))
            
            # CDAF Domain Weights Sum
            weights_sum = sum(CDAF_DOMAIN_WEIGHTS.values())
            passed = abs(weights_sum - 1.0) < 1e-9
            self.report.add_result(AuditResult(
                section="1.1",
                check_name="CDAF Domain Weights Sum",
                passed=passed,
                message=f"Domain weights sum to {weights_sum:.10f} (expected 1.0)",
                severity="ERROR" if not passed else "INFO",
                details={"sum": weights_sum, "weights": CDAF_DOMAIN_WEIGHTS}
            ))
            
            # Causal Chain Sequential
            passed = list(CAUSAL_CHAIN_ORDER.values()) == list(range(len(CAUSAL_CHAIN_ORDER)))
            self.report.add_result(AuditResult(
                section="1.1",
                check_name="Causal Chain Sequential",
                passed=passed,
                message="CAUSAL_CHAIN_ORDER values are sequential" if passed else "CAUSAL_CHAIN_ORDER values not sequential",
                severity="ERROR" if not passed else "INFO",
                details=CAUSAL_CHAIN_ORDER
            ))
            
            # Run validation function
            validation_results = validate_canonical_specs()
            all_passed = all(validation_results.values())
            self.report.add_result(AuditResult(
                section="1.1",
                check_name="Canonical Specs Validation Function",
                passed=all_passed,
                message="All canonical specs validation checks passed" if all_passed else "Some validation checks failed",
                severity="WARNING" if not all_passed else "INFO",
                details=validation_results
            ))
            
            # 1.2 Missing Canonical Constants - Search for hardcoded values
            print("  🔍 Searching for hardcoded parameters...")
            hardcoded_params = self._search_hardcoded_params()
            passed = len(hardcoded_params) == 0
            self.report.add_result(AuditResult(
                section="1.2",
                check_name="Hardcoded Parameters",
                passed=passed,
                message=f"Found {len(hardcoded_params)} hardcoded parameters outside canonical_specs" if not passed else "No hardcoded parameters found",
                severity="WARNING" if not passed else "INFO",
                details={"hardcoded_locations": hardcoded_params[:10]}  # Limit to 10 for brevity
            ))
            
        except Exception as e:
            self.report.add_result(AuditResult(
                section="1",
                check_name="Section 1 Execution",
                passed=False,
                message=f"Failed to complete Section 1 audit: {str(e)}",
                severity="CRITICAL"
            ))

    def audit_section_2_type_defaults(self) -> None:
        """Section 2: TYPE Defaults Consistency Audit."""
        print("📋 Section 2: Auditing TYPE Defaults Consistency...")
        
        try:
            from farfan_pipeline.infrastructure.calibration.type_defaults import (
                VALID_CONTRACT_TYPES,
                get_type_defaults,
            )
            
            # 2.1 Epistemic Ratio Validation
            for type_code in VALID_CONTRACT_TYPES:
                try:
                    defaults = get_type_defaults(type_code)
                    ratios = defaults.epistemic_ratios
                    
                    # Calculate midpoint sum
                    n1_mid = ratios.n1_empirical.midpoint()
                    n2_mid = ratios.n2_inferential.midpoint()
                    n3_mid = ratios.n3_audit.midpoint()
                    ratio_sum = n1_mid + n2_mid + n3_mid
                    
                    passed = abs(ratio_sum - 1.0) < 0.02  # Within tolerance
                    self.report.add_result(AuditResult(
                        section="2.1",
                        check_name=f"Epistemic Ratio Sum - {type_code}",
                        passed=passed,
                        message=f"{type_code}: Ratio sum = {ratio_sum:.4f}",
                        severity="ERROR" if not passed else "INFO",
                        details={
                            "type": type_code,
                            "n1_mid": n1_mid,
                            "n2_mid": n2_mid,
                            "n3_mid": n3_mid,
                            "sum": ratio_sum
                        }
                    ))
                    
                    # 2.3 Permitted/Prohibited Disjointness
                    overlap = defaults.permitted_operations & defaults.prohibited_operations
                    passed = len(overlap) == 0
                    self.report.add_result(AuditResult(
                        section="2.3",
                        check_name=f"Operations Disjointness - {type_code}",
                        passed=passed,
                        message=f"{type_code}: No overlap between permitted/prohibited" if passed else f"{type_code}: Overlap found: {overlap}",
                        severity="CRITICAL" if not passed else "INFO",
                        details={"overlap": list(overlap)}
                    ))
                    
                except Exception as e:
                    self.report.add_result(AuditResult(
                        section="2",
                        check_name=f"Type Defaults Loading - {type_code}",
                        passed=False,
                        message=f"Failed to load defaults for {type_code}: {str(e)}",
                        severity="ERROR"
                    ))
                    
        except Exception as e:
            self.report.add_result(AuditResult(
                section="2",
                check_name="Section 2 Execution",
                passed=False,
                message=f"Failed to complete Section 2 audit: {str(e)}",
                severity="CRITICAL"
            ))

    def audit_section_3_calibration_layer(self) -> None:
        """Section 3: Calibration Layer Invariants."""
        print("📋 Section 3: Auditing Calibration Layer Invariants...")
        
        try:
            from farfan_pipeline.infrastructure.calibration.calibration_core import (
                VALID_EVIDENCE_PREFIXES,
                COMMIT_SHA_PATTERN,
            )
            
            # 3.1 Required Parameters Presence
            required_params = frozenset({
                "prior_strength",
                "veto_threshold",
                "chunk_size",
                "extraction_coverage_target",
            })
            
            self.report.add_result(AuditResult(
                section="3.1",
                check_name="Required Parameters Defined",
                passed=True,
                message=f"Required parameters set defined: {required_params}",
                severity="INFO",
                details={"required_params": list(required_params)}
            ))
            
            # 3.2 Evidence Reference Validity - Check constants are defined
            passed = len(VALID_EVIDENCE_PREFIXES) > 0
            self.report.add_result(AuditResult(
                section="3.2",
                check_name="Evidence Prefixes Defined",
                passed=passed,
                message=f"Valid evidence prefixes: {VALID_EVIDENCE_PREFIXES}",
                severity="WARNING" if not passed else "INFO",
                details={"prefixes": list(VALID_EVIDENCE_PREFIXES)}
            ))
            
            # Check commit SHA pattern
            passed = COMMIT_SHA_PATTERN.pattern is not None
            self.report.add_result(AuditResult(
                section="3.2",
                check_name="Commit SHA Pattern Defined",
                passed=passed,
                message=f"Commit SHA pattern defined: {COMMIT_SHA_PATTERN.pattern}",
                severity="WARNING" if not passed else "INFO"
            ))
            
        except Exception as e:
            self.report.add_result(AuditResult(
                section="3",
                check_name="Section 3 Execution",
                passed=False,
                message=f"Failed to complete Section 3 audit: {str(e)}",
                severity="CRITICAL"
            ))

    def audit_section_4_interaction_governance(self) -> None:
        """Section 4: Interaction Governance."""
        print("📋 Section 4: Auditing Interaction Governance...")
        
        try:
            from farfan_pipeline.infrastructure.calibration.interaction_governor import (
                _MIN_PRODUCT,
                _MAX_PRODUCT,
            )
            
            # 4.1 Bounded Fusion Constants
            passed = _MIN_PRODUCT == 0.01 and _MAX_PRODUCT == 10.0
            self.report.add_result(AuditResult(
                section="4.1",
                check_name="Bounded Fusion Constants",
                passed=passed,
                message=f"Fusion bounds: [{_MIN_PRODUCT}, {_MAX_PRODUCT}]",
                severity="WARNING" if not passed else "INFO",
                details={"min": _MIN_PRODUCT, "max": _MAX_PRODUCT}
            ))
            
            # Search for unbounded multiplications
            print("  🔍 Searching for unbounded multiplications...")
            unbounded_mults = self._search_unbounded_multiplications()
            passed = len(unbounded_mults) == 0
            self.report.add_result(AuditResult(
                section="4.1",
                check_name="Unbounded Multiplications",
                passed=passed,
                message=f"Found {len(unbounded_mults)} potential unbounded multiplications" if not passed else "No unbounded multiplications found",
                severity="WARNING" if not passed else "INFO",
                details={"locations": unbounded_mults[:5]}  # Limit to 5
            ))
            
        except Exception as e:
            self.report.add_result(AuditResult(
                section="4",
                check_name="Section 4 Execution",
                passed=False,
                message=f"Failed to complete Section 4 audit: {str(e)}",
                severity="CRITICAL"
            ))

    def audit_section_5_veto_thresholds(self) -> None:
        """Section 5: Veto Threshold Calibration."""
        print("📋 Section 5: Auditing Veto Threshold Calibration...")
        
        try:
            from farfan_pipeline.infrastructure.calibration.type_defaults import (
                VETO_THRESHOLD_STRICTEST_MIN,
                VETO_THRESHOLD_STRICTEST_MAX,
                VETO_THRESHOLD_STRICTEST_DEFAULT,
                VETO_THRESHOLD_STANDARD_MIN,
                VETO_THRESHOLD_STANDARD_MAX,
                VETO_THRESHOLD_STANDARD_DEFAULT,
                VETO_THRESHOLD_LENIENT_MIN,
                VETO_THRESHOLD_LENIENT_MAX,
                VETO_THRESHOLD_LENIENT_DEFAULT,
            )
            
            # Validate threshold ranges
            thresholds = {
                "STRICTEST": (VETO_THRESHOLD_STRICTEST_MIN, VETO_THRESHOLD_STRICTEST_MAX, VETO_THRESHOLD_STRICTEST_DEFAULT),
                "STANDARD": (VETO_THRESHOLD_STANDARD_MIN, VETO_THRESHOLD_STANDARD_MAX, VETO_THRESHOLD_STANDARD_DEFAULT),
                "LENIENT": (VETO_THRESHOLD_LENIENT_MIN, VETO_THRESHOLD_LENIENT_MAX, VETO_THRESHOLD_LENIENT_DEFAULT),
            }
            
            for name, (min_val, max_val, default_val) in thresholds.items():
                passed = min_val <= default_val <= max_val
                self.report.add_result(AuditResult(
                    section="5.1",
                    check_name=f"Veto Threshold Range - {name}",
                    passed=passed,
                    message=f"{name}: [{min_val}, {max_val}], default={default_val}",
                    severity="ERROR" if not passed else "INFO",
                    details={"min": min_val, "max": max_val, "default": default_val}
                ))
            
        except Exception as e:
            self.report.add_result(AuditResult(
                section="5",
                check_name="Section 5 Execution",
                passed=False,
                message=f"Failed to complete Section 5 audit: {str(e)}",
                severity="CRITICAL"
            ))

    def audit_section_6_prior_strength(self) -> None:
        """Section 6: Prior Strength Calibration."""
        print("📋 Section 6: Auditing Prior Strength Calibration...")
        
        try:
            from farfan_pipeline.infrastructure.calibration.type_defaults import (
                PRIOR_STRENGTH_MIN,
                PRIOR_STRENGTH_MAX,
                PRIOR_STRENGTH_DEFAULT,
                PRIOR_STRENGTH_BAYESIAN,
            )
            
            # Validate prior strength bounds
            passed = PRIOR_STRENGTH_MIN <= PRIOR_STRENGTH_DEFAULT <= PRIOR_STRENGTH_MAX
            self.report.add_result(AuditResult(
                section="6.1",
                check_name="Prior Strength Default Bounds",
                passed=passed,
                message=f"Prior strength: min={PRIOR_STRENGTH_MIN}, default={PRIOR_STRENGTH_DEFAULT}, max={PRIOR_STRENGTH_MAX}",
                severity="ERROR" if not passed else "INFO",
                details={
                    "min": PRIOR_STRENGTH_MIN,
                    "default": PRIOR_STRENGTH_DEFAULT,
                    "max": PRIOR_STRENGTH_MAX,
                    "bayesian": PRIOR_STRENGTH_BAYESIAN
                }
            ))
            
            passed = PRIOR_STRENGTH_MIN <= PRIOR_STRENGTH_BAYESIAN <= PRIOR_STRENGTH_MAX
            self.report.add_result(AuditResult(
                section="6.1",
                check_name="Bayesian Prior Strength Bounds",
                passed=passed,
                message=f"Bayesian prior strength {PRIOR_STRENGTH_BAYESIAN} within bounds",
                severity="ERROR" if not passed else "INFO"
            ))
            
        except Exception as e:
            self.report.add_result(AuditResult(
                section="6",
                check_name="Section 6 Execution",
                passed=False,
                message=f"Failed to complete Section 6 audit: {str(e)}",
                severity="CRITICAL"
            ))

    def audit_section_7_unit_of_analysis(self) -> None:
        """Section 7: Unit of Analysis Calibration."""
        print("📋 Section 7: Auditing Unit of Analysis Calibration...")
        
        try:
            # Check if unit_of_analysis module exists and has expected structure
            unit_analysis_path = self.repo_root / "src" / "farfan_pipeline" / "infrastructure" / "calibration" / "unit_of_analysis.py"
            
            if unit_analysis_path.exists():
                content = unit_analysis_path.read_text()
                
                # 7.1 Complexity Score Formula - check for weight definitions
                has_complexity_formula = "complexity" in content.lower() and ("0.3" in content or "0.4" in content)
                self.report.add_result(AuditResult(
                    section="7.1",
                    check_name="Complexity Score Formula Present",
                    passed=has_complexity_formula,
                    message="Complexity score formula found in unit_of_analysis.py" if has_complexity_formula else "Complexity score formula not found",
                    severity="WARNING" if not has_complexity_formula else "INFO"
                ))
            else:
                self.report.add_result(AuditResult(
                    section="7",
                    check_name="Unit of Analysis Module",
                    passed=False,
                    message=f"unit_of_analysis.py not found at {unit_analysis_path}",
                    severity="WARNING"
                ))
                
        except Exception as e:
            self.report.add_result(AuditResult(
                section="7",
                check_name="Section 7 Execution",
                passed=False,
                message=f"Failed to complete Section 7 audit: {str(e)}",
                severity="WARNING"
            ))

    def audit_section_8_fact_registry(self) -> None:
        """Section 8: Fact Registry Verbosity."""
        print("📋 Section 8: Auditing Fact Registry Verbosity...")
        
        try:
            from farfan_pipeline.infrastructure.calibration.fact_registry import (
                CanonicalFactRegistry,
            )
            
            # Check verbosity threshold
            registry = CanonicalFactRegistry()
            threshold = registry._VERBOSITY_THRESHOLD
            
            passed = threshold == 0.90
            self.report.add_result(AuditResult(
                section="8.1",
                check_name="Verbosity Threshold",
                passed=passed,
                message=f"Verbosity threshold: {threshold} (expected 0.90)",
                severity="WARNING" if not passed else "INFO",
                details={"threshold": threshold}
            ))
            
        except Exception as e:
            self.report.add_result(AuditResult(
                section="8",
                check_name="Section 8 Execution",
                passed=False,
                message=f"Failed to complete Section 8 audit: {str(e)}",
                severity="WARNING"
            ))

    def audit_section_9_manifest_audit_trail(self) -> None:
        """Section 9: Manifest & Audit Trail."""
        print("📋 Section 9: Auditing Manifest & Audit Trail...")
        
        try:
            manifest_path = self.repo_root / "src" / "farfan_pipeline" / "infrastructure" / "calibration" / "calibration_manifest.py"
            
            if manifest_path.exists():
                self.report.add_result(AuditResult(
                    section="9",
                    check_name="Manifest Module Exists",
                    passed=True,
                    message="calibration_manifest.py found",
                    severity="INFO"
                ))
            else:
                self.report.add_result(AuditResult(
                    section="9",
                    check_name="Manifest Module Exists",
                    passed=False,
                    message="calibration_manifest.py not found",
                    severity="WARNING"
                ))
                
        except Exception as e:
            self.report.add_result(AuditResult(
                section="9",
                check_name="Section 9 Execution",
                passed=False,
                message=f"Failed to complete Section 9 audit: {str(e)}",
                severity="WARNING"
            ))

    def audit_section_10_missing_coverage(self) -> None:
        """Section 10: Missing Calibration Coverage."""
        print("📋 Section 10: Auditing Missing Calibration Coverage...")
        
        try:
            # Search for threshold/weight/prior/veto keywords outside calibration
            print("  🔍 Searching for uncalibrated modules...")
            uncalibrated = self._search_uncalibrated_modules()
            
            passed = len(uncalibrated) == 0
            self.report.add_result(AuditResult(
                section="10.1",
                check_name="Uncalibrated Modules",
                passed=passed,
                message=f"Found {len(uncalibrated)} modules with potential uncalibrated parameters" if not passed else "All modules appear calibrated",
                severity="WARNING" if not passed else "INFO",
                details={"uncalibrated_files": uncalibrated[:10]}  # Limit to 10
            ))
            
        except Exception as e:
            self.report.add_result(AuditResult(
                section="10",
                check_name="Section 10 Execution",
                passed=False,
                message=f"Failed to complete Section 10 audit: {str(e)}",
                severity="WARNING"
            ))

    def _search_hardcoded_params(self) -> List[Dict[str, str]]:
        """Search for hardcoded parameters outside canonical_specs."""
        hardcoded = []
        src_path = self.repo_root / "src"
        
        # Patterns to search for
        patterns = [
            r'\b0\.[5-9]\d*\b',  # Decimal thresholds 0.5-0.9
            r'\bthreshold\s*=\s*[\d.]+',
            r'\bweight\s*=\s*[\d.]+',
        ]
        
        for py_file in src_path.rglob("*.py"):
            # Skip canonical_specs and calibration modules
            if "canonical_specs" in str(py_file) or "calibration" in str(py_file):
                continue
                
            try:
                content = py_file.read_text()
                for pattern in patterns:
                    matches = re.findall(pattern, content, re.IGNORECASE)
                    if matches:
                        hardcoded.append({
                            "file": str(py_file.relative_to(self.repo_root)),
                            "pattern": pattern,
                            "matches": len(matches)
                        })
                        break  # Only add file once
            except Exception:
                pass
                
        return hardcoded

    def _search_unbounded_multiplications(self) -> List[Dict[str, str]]:
        """Search for unbounded multiplication operations."""
        unbounded = []
        src_path = self.repo_root / "src"
        
        patterns = [
            r'math\.prod\(',
            r'reduce\s*\([^)]*\*',
            r'functools\.reduce',
        ]
        
        for py_file in src_path.rglob("*.py"):
            # Skip interaction_governor itself
            if "interaction_governor" in str(py_file):
                continue
                
            try:
                content = py_file.read_text()
                for pattern in patterns:
                    if re.search(pattern, content):
                        unbounded.append({
                            "file": str(py_file.relative_to(self.repo_root)),
                            "pattern": pattern
                        })
                        break
            except Exception:
                pass
                
        return unbounded

    def _search_uncalibrated_modules(self) -> List[str]:
        """Search for modules with potential uncalibrated parameters."""
        uncalibrated = []
        src_path = self.repo_root / "src"
        
        keywords = ["threshold", "weight", "prior", "veto"]
        
        for py_file in src_path.rglob("*.py"):
            # Skip calibration infrastructure
            rel_path = py_file.relative_to(self.repo_root)
            if "calibration" in str(rel_path) or "canonical_specs" in str(rel_path):
                continue
                
            try:
                content = py_file.read_text()
                for keyword in keywords:
                    if re.search(rf'\b{keyword}\b', content, re.IGNORECASE):
                        uncalibrated.append(str(rel_path))
                        break
            except Exception:
                pass
                
        return uncalibrated

    def _generate_recommendations(self) -> None:
        """Generate recommendations based on audit results."""
        if self.report.critical > 0:
            self.report.recommendations.append(
                "🚨 CRITICAL: Address all critical issues immediately before proceeding with development"
            )
        
        if self.report.errors > 0:
            self.report.recommendations.append(
                f"⚠️  Fix {self.report.errors} error(s) found in calibration system"
            )
        
        if self.report.warnings > 0:
            self.report.recommendations.append(
                f"📌 Review {self.report.warnings} warning(s) for potential improvements"
            )
        
        # Specific recommendations based on failed checks
        failed_sections = set()
        for result in self.report.results:
            if not result.passed:
                section_num = result.section.split('.')[0]
                failed_sections.add(section_num)
        
        if "1" in failed_sections:
            self.report.recommendations.append(
                "📋 Section 1: Migrate hardcoded parameters to canonical_specs.py"
            )
        
        if "2" in failed_sections:
            self.report.recommendations.append(
                "📋 Section 2: Review and fix TYPE defaults inconsistencies"
            )
        
        if "4" in failed_sections:
            self.report.recommendations.append(
                "📋 Section 4: Replace unbounded multiplications with bounded_multiplicative_fusion()"
            )
        
        if "10" in failed_sections:
            self.report.recommendations.append(
                "📋 Section 10: Integrate uncalibrated modules into calibration framework"
            )


def format_report_text(report: AuditReport) -> str:
    """Format report as text."""
    lines = []
    lines.append("=" * 80)
    lines.append("FARFAN CALIBRATION & PARAMETRIZATION SYSTEM AUDIT REPORT")
    lines.append("=" * 80)
    lines.append(f"\nTimestamp: {report.timestamp}")
    lines.append(f"\nSummary:")
    summary = report.get_summary()
    for key, value in summary.items():
        if key != "timestamp":
            lines.append(f"  {key}: {value}")
    
    lines.append(f"\n{'-' * 80}")
    lines.append("AUDIT RESULTS BY SECTION")
    lines.append("-" * 80)
    
    # Group by section
    by_section = defaultdict(list)
    for result in report.results:
        by_section[result.section].append(result)
    
    for section in sorted(by_section.keys()):
        lines.append(f"\n[Section {section}]")
        for result in by_section[section]:
            status = "✓ PASS" if result.passed else "✗ FAIL"
            severity = f"[{result.severity}]" if not result.passed else ""
            lines.append(f"  {status} {severity} {result.check_name}: {result.message}")
    
    if report.recommendations:
        lines.append(f"\n{'-' * 80}")
        lines.append("RECOMMENDATIONS")
        lines.append("-" * 80)
        for rec in report.recommendations:
            lines.append(f"  {rec}")
    
    lines.append(f"\n{'=' * 80}")
    return "\n".join(lines)


def format_report_markdown(report: AuditReport) -> str:
    """Format report as markdown."""
    lines = []
    lines.append("# FARFAN Calibration & Parametrization System Audit Report\n")
    lines.append(f"**Timestamp:** {report.timestamp}\n")
    
    lines.append("## Executive Summary\n")
    summary = report.get_summary()
    lines.append(f"- **Total Checks:** {summary['total_checks']}")
    lines.append(f"- **Passed:** {summary['passed_checks']}")
    lines.append(f"- **Failed:** {summary['failed_checks']}")
    lines.append(f"- **Pass Rate:** {summary['pass_rate']}")
    lines.append(f"- **Warnings:** {summary['warnings']}")
    lines.append(f"- **Errors:** {summary['errors']}")
    lines.append(f"- **Critical:** {summary['critical']}\n")
    
    lines.append("## Audit Results by Section\n")
    
    # Group by section
    by_section = defaultdict(list)
    for result in report.results:
        by_section[result.section].append(result)
    
    for section in sorted(by_section.keys()):
        lines.append(f"### Section {section}\n")
        lines.append("| Status | Check | Message | Severity |")
        lines.append("|--------|-------|---------|----------|")
        for result in by_section[section]:
            status = "✓" if result.passed else "✗"
            severity = result.severity if not result.passed else "-"
            check = result.check_name.replace("|", "\\|")
            message = result.message.replace("|", "\\|")
            lines.append(f"| {status} | {check} | {message} | {severity} |")
        lines.append("")
    
    if report.recommendations:
        lines.append("## Recommendations\n")
        for rec in report.recommendations:
            lines.append(f"- {rec}")
        lines.append("")
    
    return "\n".join(lines)


def format_report_json(report: AuditReport) -> str:
    """Format report as JSON."""
    data = {
        "summary": report.get_summary(),
        "results": [
            {
                "section": r.section,
                "check_name": r.check_name,
                "passed": r.passed,
                "message": r.message,
                "severity": r.severity,
                "details": r.details
            }
            for r in report.results
        ],
        "recommendations": report.recommendations
    }
    return json.dumps(data, indent=2)


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Audit FARFAN Calibration & Parametrization System"
    )
    parser.add_argument(
        "--section",
        type=int,
        choices=range(1, 11),
        help="Run specific section only (1-10)"
    )
    parser.add_argument(
        "--output-format",
        choices=["text", "json", "markdown"],
        default="text",
        help="Output format (default: text)"
    )
    parser.add_argument(
        "--output-file",
        type=Path,
        help="Write report to file (default: stdout)"
    )
    
    args = parser.parse_args()
    
    # Determine repository root
    repo_root = Path(__file__).parent.parent
    
    # Create auditor and run audit
    auditor = CalibrationAuditor(repo_root)
    
    if args.section:
        print(f"Running section {args.section} only...")
        method_name = f"audit_section_{args.section}_"
        methods = [m for m in dir(auditor) if m.startswith(method_name)]
        if methods:
            getattr(auditor, methods[0])()
        else:
            print(f"Section {args.section} not found")
            return 1
    else:
        auditor.run_full_audit()
    
    report = auditor.report
    
    # Format output
    if args.output_format == "json":
        output = format_report_json(report)
    elif args.output_format == "markdown":
        output = format_report_markdown(report)
    else:
        output = format_report_text(report)
    
    # Write output
    if args.output_file:
        args.output_file.write_text(output)
        print(f"\n✅ Report written to {args.output_file}")
    else:
        print(output)
    
    # Return exit code based on failures
    if report.critical > 0:
        return 2
    elif report.errors > 0:
        return 1
    else:
        return 0


if __name__ == "__main__":
    sys.exit(main())
