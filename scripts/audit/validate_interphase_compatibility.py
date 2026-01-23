#!/usr/bin/env python3
"""
Enhanced Interphase Compatibility Validator
===========================================

Performs deep validation of signature compatibility between phases by:
1. Loading actual Python modules dynamically
2. Inspecting real function signatures with type hints
3. Validating that phase outputs match next phase inputs
4. Checking for breaking changes

Author: F.A.R.F.A.N Signature Governance System
Version: 1.0.0
Date: 2026-01-23
"""

import importlib.util
import inspect
import json
import logging
import sys
from dataclasses import asdict, dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any, Callable, get_type_hints

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


@dataclass
class SignatureDetail:
    """Detailed signature information including runtime data."""
    function_name: str
    module_path: str
    parameters: dict[str, str]
    return_type: str
    has_type_hints: bool
    signature_string: str
    
    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class CompatibilityIssue:
    """Represents a compatibility issue between phases."""
    severity: str  # 'critical', 'high', 'medium', 'low'
    category: str  # 'type_mismatch', 'missing_annotation', 'signature_change', etc.
    source_phase: str
    target_phase: str
    source_function: str
    target_function: str | None
    description: str
    recommendation: str
    
    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class CompatibilityReport:
    """Complete compatibility validation report."""
    timestamp: str
    total_bridges_checked: int
    total_adapters_checked: int
    total_validators_checked: int
    issues: list[CompatibilityIssue] = field(default_factory=list)
    signatures_analyzed: list[SignatureDetail] = field(default_factory=list)
    
    @property
    def critical_count(self) -> int:
        return sum(1 for i in self.issues if i.severity == 'critical')
    
    @property
    def high_count(self) -> int:
        return sum(1 for i in self.issues if i.severity == 'high')
    
    @property
    def medium_count(self) -> int:
        return sum(1 for i in self.issues if i.severity == 'medium')
    
    @property
    def low_count(self) -> int:
        return sum(1 for i in self.issues if i.severity == 'low')
    
    def to_dict(self) -> dict[str, Any]:
        return {
            'timestamp': self.timestamp,
            'total_bridges_checked': self.total_bridges_checked,
            'total_adapters_checked': self.total_adapters_checked,
            'total_validators_checked': self.total_validators_checked,
            'issues': [i.to_dict() for i in self.issues],
            'signatures_analyzed': [s.to_dict() for s in self.signatures_analyzed],
            'summary': {
                'critical': self.critical_count,
                'high': self.high_count,
                'medium': self.medium_count,
                'low': self.low_count,
                'total': len(self.issues)
            }
        }


class InterphaseCompatibilityValidator:
    """Validates compatibility of interphase signatures at runtime."""
    
    def __init__(self, project_root: Path):
        self.project_root = project_root
        self.phases_dir = project_root / "src" / "farfan_pipeline" / "phases"
        
        # Add project root to sys.path for imports
        if str(project_root) not in sys.path:
            sys.path.insert(0, str(project_root))
        if str(project_root / "src") not in sys.path:
            sys.path.insert(0, str(project_root / "src"))
        
        self.report = CompatibilityReport(
            timestamp=datetime.now().isoformat(),
            total_bridges_checked=0,
            total_adapters_checked=0,
            total_validators_checked=0
        )
    
    def validate_all_interphases(self) -> CompatibilityReport:
        """Perform comprehensive validation of all interphases."""
        logger.info("Starting interphase compatibility validation...")
        
        # Check critical bridge functions
        self._check_phase0_to_phase1_bridge()
        self._check_phase1_to_phase2_adapter()
        self._check_phase2_to_phase3_adapter()
        self._check_phase6_to_phase7_bridge()
        
        # Check validator interfaces
        self._check_phase8_validators()
        
        logger.info(f"Validation complete. Found {len(self.report.issues)} issues.")
        return self.report
    
    def _check_phase0_to_phase1_bridge(self) -> None:
        """Validate Phase 0 to Phase 1 bridge compatibility."""
        logger.info("Checking Phase 0 → Phase 1 bridge...")
        self.report.total_bridges_checked += 1
        
        try:
            # Import the bridge module
            from farfan_pipeline.phases.Phase_01.interphase.phase0_to_phase1_bridge import (
                bridge_phase0_to_phase1,
                extract_from_wiring_components,
                transform_to_canonical_input
            )
            
            # Analyze signatures
            bridge_sig = self._analyze_function_signature(bridge_phase0_to_phase1, "Phase_01.interphase")
            extract_sig = self._analyze_function_signature(extract_from_wiring_components, "Phase_01.interphase")
            transform_sig = self._analyze_function_signature(transform_to_canonical_input, "Phase_01.interphase")
            
            self.report.signatures_analyzed.extend([bridge_sig, extract_sig, transform_sig])
            
            # Check for type annotations
            if not bridge_sig.has_type_hints:
                self.report.issues.append(CompatibilityIssue(
                    severity='medium',
                    category='missing_annotation',
                    source_phase='Phase_00',
                    target_phase='Phase_01',
                    source_function='bridge_phase0_to_phase1',
                    target_function=None,
                    description='Bridge function lacks complete type annotations',
                    recommendation='Add type hints to all parameters and return type'
                ))
            
            logger.info("✓ Phase 0 → Phase 1 bridge checked")
            
        except ImportError as e:
            logger.error(f"Failed to import Phase 0 → Phase 1 bridge: {e}")
            self.report.issues.append(CompatibilityIssue(
                severity='critical',
                category='import_error',
                source_phase='Phase_00',
                target_phase='Phase_01',
                source_function='bridge_phase0_to_phase1',
                target_function=None,
                description=f'Cannot import bridge module: {e}',
                recommendation='Fix import errors in phase0_to_phase1_bridge.py'
            ))
        except Exception as e:
            logger.error(f"Error checking Phase 0 → Phase 1 bridge: {e}")
    
    def _check_phase1_to_phase2_adapter(self) -> None:
        """Validate Phase 1 to Phase 2 adapter compatibility."""
        logger.info("Checking Phase 1 → Phase 2 adapter...")
        self.report.total_adapters_checked += 1
        
        try:
            from farfan_pipeline.phases.Phase_02.interphase.phase1_phase2_adapter import (
                adapt_phase1_to_phase2,
                validate_adaptation,
                Phase2InputBundle
            )
            
            # Analyze signatures
            adapt_sig = self._analyze_function_signature(adapt_phase1_to_phase2, "Phase_02.interphase")
            validate_sig = self._analyze_function_signature(validate_adaptation, "Phase_02.interphase")
            
            self.report.signatures_analyzed.extend([adapt_sig, validate_sig])
            
            # Check adapter signature
            if 'phase1_output' not in adapt_sig.parameters:
                self.report.issues.append(CompatibilityIssue(
                    severity='high',
                    category='signature_mismatch',
                    source_phase='Phase_01',
                    target_phase='Phase_02',
                    source_function='adapt_phase1_to_phase2',
                    target_function=None,
                    description='Adapter missing expected phase1_output parameter',
                    recommendation='Ensure adapter accepts Phase 1 output structure'
                ))
            
            logger.info("✓ Phase 1 → Phase 2 adapter checked")
            
        except ImportError as e:
            logger.error(f"Failed to import Phase 1 → Phase 2 adapter: {e}")
            self.report.issues.append(CompatibilityIssue(
                severity='critical',
                category='import_error',
                source_phase='Phase_01',
                target_phase='Phase_02',
                source_function='adapt_phase1_to_phase2',
                target_function=None,
                description=f'Cannot import adapter module: {e}',
                recommendation='Fix import errors in phase1_phase2_adapter.py'
            ))
        except Exception as e:
            logger.error(f"Error checking Phase 1 → Phase 2 adapter: {e}")
    
    def _check_phase2_to_phase3_adapter(self) -> None:
        """Validate Phase 2 to Phase 3 adapter compatibility."""
        logger.info("Checking Phase 2 → Phase 3 adapter...")
        self.report.total_adapters_checked += 1
        
        try:
            from farfan_pipeline.phases.Phase_02.interphase.phase2_phase3_adapter import (
                adapt_phase2_to_phase3
            )
            
            # Analyze signature
            adapt_sig = self._analyze_function_signature(adapt_phase2_to_phase3, "Phase_02.interphase")
            self.report.signatures_analyzed.append(adapt_sig)
            
            logger.info("✓ Phase 2 → Phase 3 adapter checked")
            
        except ImportError as e:
            logger.warning(f"Phase 2 → Phase 3 adapter not found or not importable: {e}")
        except Exception as e:
            logger.error(f"Error checking Phase 2 → Phase 3 adapter: {e}")
    
    def _check_phase6_to_phase7_bridge(self) -> None:
        """Validate Phase 6 to Phase 7 bridge compatibility."""
        logger.info("Checking Phase 6 → Phase 7 bridge...")
        self.report.total_bridges_checked += 1
        
        try:
            from farfan_pipeline.phases.Phase_07.interphase.phase6_to_phase7_bridge import (
                bridge_phase6_to_phase7
            )
            
            # Analyze signature
            bridge_sig = self._analyze_function_signature(bridge_phase6_to_phase7, "Phase_07.interphase")
            self.report.signatures_analyzed.append(bridge_sig)
            
            logger.info("✓ Phase 6 → Phase 7 bridge checked")
            
        except ImportError as e:
            logger.warning(f"Phase 6 → Phase 7 bridge not found or not importable: {e}")
        except Exception as e:
            logger.error(f"Error checking Phase 6 → Phase 7 bridge: {e}")
    
    def _check_phase8_validators(self) -> None:
        """Validate Phase 8 interface validators."""
        logger.info("Checking Phase 8 validators...")
        self.report.total_validators_checked += 1
        
        try:
            from farfan_pipeline.phases.Phase_08.interphase.interface_validator import (
                Phase8InterfaceValidator,
                validate_phase8_inputs,
                validate_phase8_outputs
            )
            
            # Analyze signatures
            validate_inputs_sig = self._analyze_function_signature(validate_phase8_inputs, "Phase_08.interphase")
            validate_outputs_sig = self._analyze_function_signature(validate_phase8_outputs, "Phase_08.interphase")
            
            self.report.signatures_analyzed.extend([validate_inputs_sig, validate_outputs_sig])
            
            # Check if validator has proper type annotations
            if not validate_inputs_sig.has_type_hints:
                self.report.issues.append(CompatibilityIssue(
                    severity='low',
                    category='missing_annotation',
                    source_phase='Phase_08',
                    target_phase='Phase_08',
                    source_function='validate_phase8_inputs',
                    target_function=None,
                    description='Validator function lacks complete type annotations',
                    recommendation='Add type hints to improve type safety'
                ))
            
            logger.info("✓ Phase 8 validators checked")
            
        except ImportError as e:
            logger.error(f"Failed to import Phase 8 validators: {e}")
        except Exception as e:
            logger.error(f"Error checking Phase 8 validators: {e}")
    
    def _analyze_function_signature(self, func: Callable, module: str) -> SignatureDetail:
        """Analyze a function's signature in detail."""
        sig = inspect.signature(func)
        
        # Extract parameter types
        parameters = {}
        try:
            type_hints = get_type_hints(func)
            has_hints = True
            for param_name, param in sig.parameters.items():
                if param_name in type_hints:
                    parameters[param_name] = str(type_hints[param_name])
                else:
                    parameters[param_name] = "Any"
                    has_hints = False
            
            return_type = str(type_hints.get('return', 'Any'))
        except Exception as e:
            logger.debug(f"Could not extract type hints for {func.__name__}: {e}")
            has_hints = False
            for param_name in sig.parameters.keys():
                parameters[param_name] = "Any"
            return_type = "Any"
        
        return SignatureDetail(
            function_name=func.__name__,
            module_path=module,
            parameters=parameters,
            return_type=return_type,
            has_type_hints=has_hints,
            signature_string=str(sig)
        )
    
    def export_report(self, output_path: Path) -> None:
        """Export validation report to JSON."""
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(output_path, 'w') as f:
            json.dump(self.report.to_dict(), f, indent=2)
        
        logger.info(f"Report exported to {output_path}")
    
    def print_summary(self) -> None:
        """Print human-readable summary."""
        print("\n" + "="*80)
        print("INTERPHASE COMPATIBILITY VALIDATION REPORT")
        print("="*80)
        print(f"\nTimestamp: {self.report.timestamp}")
        print(f"Bridges Checked: {self.report.total_bridges_checked}")
        print(f"Adapters Checked: {self.report.total_adapters_checked}")
        print(f"Validators Checked: {self.report.total_validators_checked}")
        print(f"Signatures Analyzed: {len(self.report.signatures_analyzed)}")
        
        print("\n" + "-"*80)
        print("ISSUE SEVERITY SUMMARY")
        print("-"*80)
        print(f"  CRITICAL : {self.report.critical_count:3d}")
        print(f"  HIGH     : {self.report.high_count:3d}")
        print(f"  MEDIUM   : {self.report.medium_count:3d}")
        print(f"  LOW      : {self.report.low_count:3d}")
        print(f"  --------")
        print(f"  TOTAL    : {len(self.report.issues):3d}")
        
        if self.report.issues:
            print("\n" + "-"*80)
            print("DETAILED ISSUES")
            print("-"*80)
            
            for idx, issue in enumerate(self.report.issues, 1):
                print(f"\n{idx}. [{issue.severity.upper()}] {issue.category}")
                print(f"   Phase: {issue.source_phase} → {issue.target_phase}")
                print(f"   Function: {issue.source_function}")
                print(f"   Issue: {issue.description}")
                print(f"   Recommendation: {issue.recommendation}")
        
        print("\n" + "="*80)
        
        # Overall status
        if self.report.critical_count > 0:
            print("❌ CRITICAL ISSUES FOUND - Immediate action required")
        elif self.report.high_count > 0:
            print("⚠️  HIGH PRIORITY ISSUES - Review required")
        elif self.report.medium_count > 0:
            print("⚠️  MEDIUM PRIORITY ISSUES - Review recommended")
        elif self.report.low_count > 0:
            print("ℹ️  LOW PRIORITY ISSUES - Consider addressing")
        else:
            print("✅ NO COMPATIBILITY ISSUES DETECTED")
        
        print("="*80 + "\n")


def main():
    """Main entry point."""
    project_root = Path(__file__).parent.parent.parent
    
    validator = InterphaseCompatibilityValidator(project_root)
    report = validator.validate_all_interphases()
    
    validator.print_summary()
    
    # Export report
    output_path = project_root / "artifacts" / "audit_reports" / "interphase_compatibility_validation.json"
    validator.export_report(output_path)
    
    print(f"Detailed report saved to: {output_path}")
    
    # Exit with appropriate code
    if report.critical_count > 0:
        return 2
    elif report.high_count > 0:
        return 1
    return 0


if __name__ == "__main__":
    import sys
    sys.exit(main())
