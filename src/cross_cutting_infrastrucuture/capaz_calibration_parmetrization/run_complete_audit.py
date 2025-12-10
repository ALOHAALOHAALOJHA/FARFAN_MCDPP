"""
Master Audit Runner.

Executes all audit tools and generates comprehensive system audit report.
"""

import json
import sys
from pathlib import Path
from datetime import datetime
from typing import Dict, Any

from comprehensive_calibration_audit import ComprehensiveCalibrationAuditor
from layer_implementation_verifier import LayerImplementationVerifier
from hardcoded_parameter_scanner import HardcodedParameterScanner


class MasterAuditRunner:
    """Runs all audits and generates master report."""
    
    def __init__(self, base_path: str = "."):
        self.base_path = Path(base_path)
        self.output_dir = self.base_path / "artifacts/audit_reports"
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        self.timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        self.results = {}
    
    def run_comprehensive_audit(self) -> Dict[str, Any]:
        """Run comprehensive calibration audit."""
        print("\n" + "=" * 80)
        print("PHASE 1: COMPREHENSIVE CALIBRATION AUDIT")
        print("=" * 80)
        
        auditor = ComprehensiveCalibrationAuditor(str(self.base_path))
        result = auditor.run_comprehensive_audit()
        
        auditor.save_audit_results(result, str(self.output_dir))
        
        return {
            "total_methods": len(result.canonical_method_inventory),
            "methods_with_intrinsic": result.verification_report["summary"]["methods_with_intrinsic_calibration"],
            "layers_implemented": result.verification_report["summary"]["layers_implemented"],
            "missing_evaluators": len(result.missing_evaluators),
            "stub_implementations": len(result.stub_implementations),
            "parameter_violations": len(result.parameter_violations)
        }
    
    def run_layer_verification(self) -> Dict[str, Any]:
        """Run layer implementation verification."""
        print("\n" + "=" * 80)
        print("PHASE 2: LAYER IMPLEMENTATION VERIFICATION")
        print("=" * 80)
        
        calibration_dir = self.base_path / "src/cross_cutting_infrastrucuture/capaz_calibration_parmetrization/calibration"
        verifier = LayerImplementationVerifier(str(calibration_dir))
        
        verifications = verifier.verify_all_layers()
        report = verifier.generate_detailed_report(verifications)
        
        verifier.print_summary(report)
        
        with open(self.output_dir / f"layer_verification_{self.timestamp}.json", 'w') as f:
            json.dump(report, f, indent=2)
        
        return {
            "total_layers": report["summary"]["total_layers"],
            "fully_implemented": report["summary"]["fully_implemented"],
            "partially_implemented": report["summary"]["partially_implemented"],
            "not_implemented": report["summary"]["not_implemented"],
            "average_quality": report["summary"]["average_quality_score"]
        }
    
    def run_parameter_scan(self) -> Dict[str, Any]:
        """Run hardcoded parameter scan."""
        print("\n" + "=" * 80)
        print("PHASE 3: HARDCODED PARAMETER SCAN")
        print("=" * 80)
        
        src_dir = self.base_path / "src"
        scanner = HardcodedParameterScanner(str(src_dir))
        
        scanner.scan_all_files()
        report = scanner.generate_compliance_report()
        
        scanner.print_summary(report)
        
        scanner.save_report(
            report, 
            str(self.output_dir / f"parameter_compliance_{self.timestamp}.json")
        )
        
        return {
            "total_files": report["summary"]["total_files_scanned"],
            "compliant_files": report["summary"]["compliant_files"],
            "total_violations": report["summary"]["total_violations"],
            "compliance_percentage": report["summary"]["compliance_percentage"]
        }
    
    def generate_master_report(self) -> Dict[str, Any]:
        """Generate master audit report."""
        master_report = {
            "audit_metadata": {
                "timestamp": datetime.now().isoformat(),
                "audit_id": f"MASTER_AUDIT_{self.timestamp}",
                "auditor": "ComprehensiveCalibrationAuditSystem",
                "version": "1.0.0"
            },
            "executive_summary": {
                "comprehensive_audit": self.results.get("comprehensive", {}),
                "layer_verification": self.results.get("layer_verification", {}),
                "parameter_compliance": self.results.get("parameter_scan", {})
            },
            "critical_findings": [],
            "recommendations": [],
            "compliance_status": "unknown"
        }
        
        comp = self.results.get("comprehensive", {})
        layer = self.results.get("layer_verification", {})
        param = self.results.get("parameter_scan", {})
        
        if comp.get("missing_evaluators", 0) > 0:
            master_report["critical_findings"].append({
                "category": "Missing Layer Evaluators",
                "severity": "critical",
                "count": comp["missing_evaluators"],
                "impact": "Cannot compute calibration scores for methods requiring these layers"
            })
        
        if comp.get("stub_implementations", 0) > 0:
            master_report["critical_findings"].append({
                "category": "Stub Implementations",
                "severity": "high",
                "count": comp["stub_implementations"],
                "impact": "Layer evaluators exist but lack production logic"
            })
        
        if layer.get("not_implemented", 0) > 0:
            master_report["critical_findings"].append({
                "category": "Unimplemented Layers",
                "severity": "critical",
                "count": layer["not_implemented"],
                "impact": "Layer files missing or non-functional"
            })
        
        if param.get("total_violations", 0) > 10:
            master_report["critical_findings"].append({
                "category": "Hardcoded Parameters",
                "severity": "medium",
                "count": param["total_violations"],
                "impact": "Parameters not externalized to configuration"
            })
        
        if layer.get("fully_implemented", 0) < 8:
            master_report["recommendations"].append({
                "priority": "critical",
                "recommendation": f"Complete implementation of {8 - layer.get('fully_implemented', 0)} remaining layers",
                "action": "Implement production logic for stub/missing evaluators"
            })
        
        if param.get("compliance_percentage", 0) < 80:
            master_report["recommendations"].append({
                "priority": "high",
                "recommendation": "Migrate hardcoded parameters to centralized configuration",
                "action": f"Address {param.get('total_violations', 0)} parameter violations"
            })
        
        if comp.get("methods_with_intrinsic", 0) < comp.get("total_methods", 1) * 0.9:
            master_report["recommendations"].append({
                "priority": "high",
                "recommendation": "Complete intrinsic calibration for all methods",
                "action": f"Calibrate {comp.get('total_methods', 0) - comp.get('methods_with_intrinsic', 0)} methods"
            })
        
        critical_count = len([f for f in master_report["critical_findings"] if f["severity"] == "critical"])
        high_count = len([f for f in master_report["critical_findings"] if f["severity"] == "high"])
        
        if critical_count == 0 and high_count == 0:
            master_report["compliance_status"] = "compliant"
        elif critical_count == 0:
            master_report["compliance_status"] = "acceptable_with_warnings"
        else:
            master_report["compliance_status"] = "non_compliant"
        
        return master_report
    
    def save_master_report(self, report: Dict[str, Any]) -> None:
        """Save master report."""
        output_path = self.output_dir / f"MASTER_AUDIT_REPORT_{self.timestamp}.json"
        
        with open(output_path, 'w') as f:
            json.dump(report, f, indent=2)
        
        print(f"\n✅ Master audit report saved to {output_path}")
        
        summary_path = self.output_dir / "LATEST_AUDIT_SUMMARY.txt"
        with open(summary_path, 'w') as f:
            f.write("=" * 80 + "\n")
            f.write("CALIBRATION SYSTEM AUDIT SUMMARY\n")
            f.write("=" * 80 + "\n\n")
            
            f.write(f"Audit ID: {report['audit_metadata']['audit_id']}\n")
            f.write(f"Timestamp: {report['audit_metadata']['timestamp']}\n")
            f.write(f"Compliance Status: {report['compliance_status'].upper()}\n\n")
            
            f.write("=" * 80 + "\n")
            f.write("EXECUTIVE SUMMARY\n")
            f.write("=" * 80 + "\n\n")
            
            comp = report["executive_summary"]["comprehensive_audit"]
            f.write(f"Total Methods: {comp.get('total_methods', 'N/A')}\n")
            f.write(f"Methods with Intrinsic Calibration: {comp.get('methods_with_intrinsic', 'N/A')}\n")
            f.write(f"Layers Implemented: {comp.get('layers_implemented', 'N/A')}/8\n")
            f.write(f"Missing Evaluators: {comp.get('missing_evaluators', 'N/A')}\n")
            f.write(f"Stub Implementations: {comp.get('stub_implementations', 'N/A')}\n\n")
            
            layer = report["executive_summary"]["layer_verification"]
            f.write(f"Layer Quality Average: {layer.get('average_quality', 0):.2f}\n")
            f.write(f"Fully Implemented Layers: {layer.get('fully_implemented', 'N/A')}/8\n\n")
            
            param = report["executive_summary"]["parameter_compliance"]
            f.write(f"Parameter Compliance: {param.get('compliance_percentage', 0):.1f}%\n")
            f.write(f"Total Parameter Violations: {param.get('total_violations', 'N/A')}\n\n")
            
            if report["critical_findings"]:
                f.write("=" * 80 + "\n")
                f.write("CRITICAL FINDINGS\n")
                f.write("=" * 80 + "\n\n")
                for finding in report["critical_findings"]:
                    f.write(f"⚠️  {finding['category']} ({finding['severity']})\n")
                    f.write(f"   Count: {finding['count']}\n")
                    f.write(f"   Impact: {finding['impact']}\n\n")
            
            if report["recommendations"]:
                f.write("=" * 80 + "\n")
                f.write("RECOMMENDATIONS\n")
                f.write("=" * 80 + "\n\n")
                for i, rec in enumerate(report["recommendations"], 1):
                    f.write(f"{i}. ({rec['priority']}) {rec['recommendation']}\n")
                    f.write(f"   Action: {rec['action']}\n\n")
            
            f.write("=" * 80 + "\n")
        
        print(f"✅ Summary saved to {summary_path}")
    
    def print_master_summary(self, report: Dict[str, Any]) -> None:
        """Print master summary."""
        print("\n" + "=" * 80)
        print("MASTER AUDIT SUMMARY")
        print("=" * 80)
        
        print(f"\nAudit ID: {report['audit_metadata']['audit_id']}")
        print(f"Timestamp: {report['audit_metadata']['timestamp']}")
        print(f"Compliance Status: {report['compliance_status'].upper()}")
        
        print("\n" + "=" * 80)
        print("EXECUTIVE SUMMARY")
        print("=" * 80)
        
        comp = report["executive_summary"]["comprehensive_audit"]
        print(f"\n📊 Comprehensive Audit:")
        print(f"   Total Methods: {comp.get('total_methods', 'N/A')}")
        print(f"   With Intrinsic Calibration: {comp.get('methods_with_intrinsic', 'N/A')}")
        print(f"   Layers Implemented: {comp.get('layers_implemented', 'N/A')}/8")
        print(f"   Missing Evaluators: {comp.get('missing_evaluators', 'N/A')}")
        print(f"   Stub Implementations: {comp.get('stub_implementations', 'N/A')}")
        
        layer = report["executive_summary"]["layer_verification"]
        print(f"\n🔍 Layer Verification:")
        print(f"   Fully Implemented: {layer.get('fully_implemented', 'N/A')}/8")
        print(f"   Partially Implemented: {layer.get('partially_implemented', 'N/A')}")
        print(f"   Not Implemented: {layer.get('not_implemented', 'N/A')}")
        print(f"   Average Quality: {layer.get('average_quality', 0):.2f}")
        
        param = report["executive_summary"]["parameter_compliance"]
        print(f"\n⚙️  Parameter Compliance:")
        print(f"   Files Scanned: {param.get('total_files', 'N/A')}")
        print(f"   Compliant: {param.get('compliant_files', 'N/A')}")
        print(f"   Compliance: {param.get('compliance_percentage', 0):.1f}%")
        print(f"   Violations: {param.get('total_violations', 'N/A')}")
        
        if report["critical_findings"]:
            print("\n" + "=" * 80)
            print("⚠️  CRITICAL FINDINGS")
            print("=" * 80)
            for finding in report["critical_findings"]:
                print(f"\n❌ {finding['category']} ({finding['severity']})")
                print(f"   Count: {finding['count']}")
                print(f"   Impact: {finding['impact']}")
        
        if report["recommendations"]:
            print("\n" + "=" * 80)
            print("📋 TOP RECOMMENDATIONS")
            print("=" * 80)
            for i, rec in enumerate(report["recommendations"][:5], 1):
                print(f"\n{i}. ({rec['priority'].upper()}) {rec['recommendation']}")
                print(f"   Action: {rec['action']}")
        
        print("\n" + "=" * 80)
    
    def run_all_audits(self) -> Dict[str, Any]:
        """Run all audits and generate master report."""
        print("\n" + "=" * 80)
        print("COMPREHENSIVE CALIBRATION SYSTEM AUDIT")
        print("=" * 80)
        print(f"Audit ID: MASTER_AUDIT_{self.timestamp}")
        print(f"Timestamp: {datetime.now().isoformat()}")
        print("=" * 80)
        
        self.results["comprehensive"] = self.run_comprehensive_audit()
        
        self.results["layer_verification"] = self.run_layer_verification()
        
        self.results["parameter_scan"] = self.run_parameter_scan()
        
        print("\n" + "=" * 80)
        print("GENERATING MASTER REPORT")
        print("=" * 80)
        
        master_report = self.generate_master_report()
        
        self.save_master_report(master_report)
        
        self.print_master_summary(master_report)
        
        return master_report


def main():
    """Main entry point."""
    runner = MasterAuditRunner()
    
    try:
        master_report = runner.run_all_audits()
        
        if master_report["compliance_status"] == "compliant":
            print("\n✅ AUDIT PASSED: System is compliant")
            sys.exit(0)
        elif master_report["compliance_status"] == "acceptable_with_warnings":
            print("\n⚠️  AUDIT WARNING: System has issues but is functional")
            sys.exit(0)
        else:
            print("\n❌ AUDIT FAILED: Critical issues found")
            sys.exit(1)
    
    except Exception as e:
        print(f"\n❌ AUDIT ERROR: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(2)


if __name__ == "__main__":
    main()
