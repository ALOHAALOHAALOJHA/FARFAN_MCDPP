#!/usr/bin/env python3
"""
Interphase Signature Compatibility Inspector
============================================

This script performs a comprehensive inspection of all interphase signatures
within the canonic phases (Phase 0-9) to ensure compatibility.

Purpose:
- Extract and analyze all function signatures in interphase modules
- Validate input/output contracts between adjacent phases
- Detect signature mismatches and incompatibilities
- Generate detailed compatibility report

Author: F.A.R.F.A.N Signature Governance System
Version: 1.0.0
Date: 2026-01-23
"""

import ast
import inspect
import json
import logging
from dataclasses import asdict, dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any, get_type_hints

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


@dataclass
class FunctionSignatureInfo:
    """Detailed information about a function signature."""
    module_path: str
    phase: str
    function_name: str
    parameters: list[dict[str, Any]]
    return_type: str
    is_public: bool
    docstring: str | None = None
    line_number: int = 0
    
    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class InterfaceContract:
    """Represents an interface contract between phases."""
    source_phase: str
    target_phase: str
    interface_type: str  # 'bridge', 'adapter', 'validator'
    input_signature: FunctionSignatureInfo | None = None
    output_signature: FunctionSignatureInfo | None = None
    compatibility_status: str = "unknown"  # 'compatible', 'incompatible', 'warning', 'unknown'
    issues: list[str] = field(default_factory=list)
    
    def to_dict(self) -> dict[str, Any]:
        result = {
            'source_phase': self.source_phase,
            'target_phase': self.target_phase,
            'interface_type': self.interface_type,
            'compatibility_status': self.compatibility_status,
            'issues': self.issues,
        }
        if self.input_signature:
            result['input_signature'] = self.input_signature.to_dict()
        if self.output_signature:
            result['output_signature'] = self.output_signature.to_dict()
        return result


@dataclass
class InspectionReport:
    """Complete inspection report."""
    timestamp: str
    total_phases: int
    total_interphase_modules: int
    total_functions: int
    total_contracts: int
    signatures: list[FunctionSignatureInfo] = field(default_factory=list)
    contracts: list[InterfaceContract] = field(default_factory=list)
    compatibility_summary: dict[str, int] = field(default_factory=dict)
    issues_summary: list[dict[str, Any]] = field(default_factory=list)
    
    def to_dict(self) -> dict[str, Any]:
        return {
            'timestamp': self.timestamp,
            'total_phases': self.total_phases,
            'total_interphase_modules': self.total_interphase_modules,
            'total_functions': self.total_functions,
            'total_contracts': self.total_contracts,
            'signatures': [sig.to_dict() for sig in self.signatures],
            'contracts': [contract.to_dict() for contract in self.contracts],
            'compatibility_summary': self.compatibility_summary,
            'issues_summary': self.issues_summary,
        }


class InterphaseSignatureInspector:
    """Inspects and validates interphase signatures across all phases."""
    
    def __init__(self, project_root: Path):
        self.project_root = project_root
        self.phases_dir = project_root / "src" / "farfan_pipeline" / "phases"
        self.signatures: list[FunctionSignatureInfo] = []
        self.contracts: list[InterfaceContract] = []
        
    def inspect_all_phases(self) -> InspectionReport:
        """Perform comprehensive inspection of all phase interphases."""
        logger.info("Starting interphase signature inspection...")
        
        # Discover all phase directories
        phase_dirs = sorted(self.phases_dir.glob("Phase_*"))
        logger.info(f"Found {len(phase_dirs)} phase directories")
        
        # Extract signatures from each phase's interphase modules
        for phase_dir in phase_dirs:
            self._inspect_phase(phase_dir)
        
        # Analyze contracts between adjacent phases
        self._analyze_contracts()
        
        # Generate report
        report = self._generate_report(len(phase_dirs))
        
        logger.info(f"Inspection complete. Found {len(self.signatures)} signatures.")
        return report
    
    def _inspect_phase(self, phase_dir: Path) -> None:
        """Inspect all interphase modules in a phase."""
        phase_name = phase_dir.name
        interphase_dir = phase_dir / "interphase"
        
        if not interphase_dir.exists():
            logger.warning(f"No interphase directory for {phase_name}")
            return
        
        # Find all Python files in interphase directory
        py_files = list(interphase_dir.glob("*.py"))
        logger.info(f"Inspecting {len(py_files)} files in {phase_name}/interphase")
        
        for py_file in py_files:
            if py_file.name == "__init__.py":
                continue
            self._extract_signatures_from_file(py_file, phase_name)
    
    def _extract_signatures_from_file(self, file_path: Path, phase: str) -> None:
        """Extract function signatures from a Python file using AST."""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                source = f.read()
            
            tree = ast.parse(source, filename=str(file_path))
            
            # Extract function definitions
            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef):
                    sig_info = self._extract_function_info(node, file_path, phase)
                    if sig_info:
                        self.signatures.append(sig_info)
                        
        except Exception as e:
            logger.error(f"Failed to parse {file_path}: {e}")
    
    def _extract_function_info(
        self, 
        node: ast.FunctionDef, 
        file_path: Path, 
        phase: str
    ) -> FunctionSignatureInfo | None:
        """Extract detailed function information from AST node."""
        try:
            # Get parameter information
            parameters = []
            for arg in node.args.args:
                param_info = {
                    'name': arg.arg,
                    'type': self._extract_type_annotation(arg.annotation),
                    'kind': 'positional_or_keyword'
                }
                parameters.append(param_info)
            
            # Get return type
            return_type = self._extract_type_annotation(node.returns)
            
            # Get docstring
            docstring = ast.get_docstring(node)
            
            # Check if function is public (doesn't start with _)
            is_public = not node.name.startswith('_')
            
            return FunctionSignatureInfo(
                module_path=str(file_path.relative_to(self.project_root)),
                phase=phase,
                function_name=node.name,
                parameters=parameters,
                return_type=return_type,
                is_public=is_public,
                docstring=docstring,
                line_number=node.lineno
            )
        except Exception as e:
            logger.error(f"Failed to extract function info for {node.name}: {e}")
            return None
    
    def _extract_type_annotation(self, annotation: ast.expr | None) -> str:
        """Extract type annotation as string from AST node."""
        if annotation is None:
            return "Any"
        
        try:
            return ast.unparse(annotation)
        except Exception:
            return "Any"
    
    def _analyze_contracts(self) -> None:
        """Analyze interface contracts between phases."""
        logger.info("Analyzing interface contracts...")
        
        # Group signatures by phase
        phase_signatures: dict[str, list[FunctionSignatureInfo]] = {}
        for sig in self.signatures:
            if sig.phase not in phase_signatures:
                phase_signatures[sig.phase] = []
            phase_signatures[sig.phase].append(sig)
        
        # Identify contracts between adjacent phases
        for sig in self.signatures:
            # Check for bridge functions (phase X to phase Y)
            if 'bridge' in sig.function_name.lower():
                contract = self._create_bridge_contract(sig)
                if contract:
                    self.contracts.append(contract)
            
            # Check for adapter functions
            elif 'adapt' in sig.function_name.lower():
                contract = self._create_adapter_contract(sig)
                if contract:
                    self.contracts.append(contract)
            
            # Check for validator functions
            elif 'validate' in sig.function_name.lower() or 'validator' in sig.module_path.lower():
                contract = self._create_validator_contract(sig)
                if contract:
                    self.contracts.append(contract)
    
    def _create_bridge_contract(self, sig: FunctionSignatureInfo) -> InterfaceContract | None:
        """Create a contract for bridge functions."""
        # Extract source and target phases from function name or module
        # E.g., "bridge_phase0_to_phase1" or "phase0_to_phase1_bridge"
        func_lower = sig.function_name.lower()
        
        import re
        # Try to extract phase numbers
        match = re.search(r'phase(\d+).*phase(\d+)', func_lower)
        if match:
            source_phase = f"Phase_{int(match.group(1)):02d}"
            target_phase = f"Phase_{int(match.group(2)):02d}"
        else:
            # Try module path
            match = re.search(r'Phase_(\d+)', sig.module_path)
            if match:
                phase_num = int(match.group(1))
                source_phase = f"Phase_{phase_num:02d}"
                target_phase = f"Phase_{phase_num + 1:02d}"
            else:
                return None
        
        return InterfaceContract(
            source_phase=source_phase,
            target_phase=target_phase,
            interface_type='bridge',
            input_signature=sig,
            compatibility_status='unknown'
        )
    
    def _create_adapter_contract(self, sig: FunctionSignatureInfo) -> InterfaceContract | None:
        """Create a contract for adapter functions."""
        import re
        # Try to extract phase numbers from function name
        match = re.search(r'phase(\d+).*phase(\d+)', sig.function_name.lower())
        if match:
            source_phase = f"Phase_{int(match.group(1)):02d}"
            target_phase = f"Phase_{int(match.group(2)):02d}"
        else:
            # Use current phase as source
            match = re.search(r'Phase_(\d+)', sig.module_path)
            if match:
                phase_num = int(match.group(1))
                source_phase = f"Phase_{phase_num - 1:02d}" if phase_num > 0 else "Phase_00"
                target_phase = f"Phase_{phase_num:02d}"
            else:
                return None
        
        return InterfaceContract(
            source_phase=source_phase,
            target_phase=target_phase,
            interface_type='adapter',
            input_signature=sig,
            compatibility_status='unknown'
        )
    
    def _create_validator_contract(self, sig: FunctionSignatureInfo) -> InterfaceContract | None:
        """Create a contract for validator functions."""
        import re
        # Extract phase from module path
        match = re.search(r'Phase_(\d+)', sig.module_path)
        if match:
            phase_num = int(match.group(1))
            source_phase = f"Phase_{phase_num:02d}"
            target_phase = f"Phase_{phase_num:02d}"
        else:
            return None
        
        return InterfaceContract(
            source_phase=source_phase,
            target_phase=target_phase,
            interface_type='validator',
            input_signature=sig,
            compatibility_status='unknown'
        )
    
    def _validate_contract_compatibility(self) -> None:
        """Validate compatibility of all contracts."""
        logger.info("Validating contract compatibility...")
        
        for contract in self.contracts:
            issues = []
            
            # Check if input signature exists
            if not contract.input_signature:
                issues.append("Missing input signature")
                contract.compatibility_status = 'incompatible'
                contract.issues = issues
                continue
            
            # Validate parameter consistency
            params = contract.input_signature.parameters
            
            # Check for common anti-patterns
            if len(params) == 0:
                issues.append("Function takes no parameters - may not be an interface function")
            
            # Check for proper type annotations
            untyped_params = [p['name'] for p in params if p['type'] == 'Any']
            if untyped_params:
                issues.append(f"Parameters without type annotations: {', '.join(untyped_params)}")
            
            # Check return type
            if contract.input_signature.return_type == "Any":
                issues.append("Return type not annotated")
            
            # Set compatibility status
            if not issues:
                contract.compatibility_status = 'compatible'
            elif any('incompatible' in issue.lower() for issue in issues):
                contract.compatibility_status = 'incompatible'
            else:
                contract.compatibility_status = 'warning'
            
            contract.issues = issues
    
    def _generate_report(self, num_phases: int) -> InspectionReport:
        """Generate comprehensive inspection report."""
        # Validate contracts
        self._validate_contract_compatibility()
        
        # Count unique interphase modules
        unique_modules = len(set(sig.module_path for sig in self.signatures))
        
        # Generate compatibility summary
        compatibility_summary = {
            'compatible': sum(1 for c in self.contracts if c.compatibility_status == 'compatible'),
            'incompatible': sum(1 for c in self.contracts if c.compatibility_status == 'incompatible'),
            'warning': sum(1 for c in self.contracts if c.compatibility_status == 'warning'),
            'unknown': sum(1 for c in self.contracts if c.compatibility_status == 'unknown'),
        }
        
        # Generate issues summary
        issues_summary = []
        for contract in self.contracts:
            if contract.issues:
                issues_summary.append({
                    'contract': f"{contract.source_phase} -> {contract.target_phase}",
                    'type': contract.interface_type,
                    'issues': contract.issues,
                    'severity': contract.compatibility_status
                })
        
        return InspectionReport(
            timestamp=datetime.now().isoformat(),
            total_phases=num_phases,
            total_interphase_modules=unique_modules,
            total_functions=len(self.signatures),
            total_contracts=len(self.contracts),
            signatures=self.signatures,
            contracts=self.contracts,
            compatibility_summary=compatibility_summary,
            issues_summary=issues_summary
        )
    
    def export_report(self, report: InspectionReport, output_path: Path) -> None:
        """Export report to JSON file."""
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(output_path, 'w') as f:
            json.dump(report.to_dict(), f, indent=2)
        
        logger.info(f"Report exported to {output_path}")
    
    def print_summary(self, report: InspectionReport) -> None:
        """Print a human-readable summary to console."""
        print("\n" + "="*80)
        print("INTERPHASE SIGNATURE COMPATIBILITY INSPECTION REPORT")
        print("="*80)
        print(f"\nTimestamp: {report.timestamp}")
        print(f"Total Phases: {report.total_phases}")
        print(f"Total Interphase Modules: {report.total_interphase_modules}")
        print(f"Total Functions Analyzed: {report.total_functions}")
        print(f"Total Interface Contracts: {report.total_contracts}")
        
        print("\n" + "-"*80)
        print("COMPATIBILITY SUMMARY")
        print("-"*80)
        for status, count in report.compatibility_summary.items():
            print(f"  {status.upper():15s}: {count:3d}")
        
        if report.issues_summary:
            print("\n" + "-"*80)
            print("ISSUES DETECTED")
            print("-"*80)
            for idx, issue_info in enumerate(report.issues_summary, 1):
                print(f"\n{idx}. {issue_info['contract']} ({issue_info['type']})")
                print(f"   Severity: {issue_info['severity'].upper()}")
                for issue in issue_info['issues']:
                    print(f"   - {issue}")
        
        print("\n" + "="*80)
        
        # Overall status
        if report.compatibility_summary['incompatible'] > 0:
            print("❌ INCOMPATIBILITIES DETECTED - Action required")
        elif report.compatibility_summary['warning'] > 0:
            print("⚠️  WARNINGS DETECTED - Review recommended")
        else:
            print("✅ ALL SIGNATURES COMPATIBLE")
        print("="*80 + "\n")


def main():
    """Main entry point."""
    # Set project root
    project_root = Path(__file__).parent.parent.parent
    
    # Create inspector
    inspector = InterphaseSignatureInspector(project_root)
    
    # Run inspection
    report = inspector.inspect_all_phases()
    
    # Print summary to console
    inspector.print_summary(report)
    
    # Export detailed report
    output_path = project_root / "artifacts" / "audit_reports" / "interphase_signature_inspection.json"
    inspector.export_report(report, output_path)
    
    print(f"Detailed report saved to: {output_path}")
    
    # Exit with appropriate code
    if report.compatibility_summary['incompatible'] > 0:
        return 1
    return 0


if __name__ == "__main__":
    import sys
    sys.exit(main())
