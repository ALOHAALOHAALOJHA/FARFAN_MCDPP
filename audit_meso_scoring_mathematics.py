"""
Mathematical Audit Tool for Meso-Level Cluster Scoring

This tool performs a comprehensive mathematical audit of the ClusterAggregator
scoring procedures, specifically evaluating:
1. Mathematical correctness of aggregation formulas
2. Sensitivity to dispersion vs convergence scenarios
3. Granularity and adaptability of penalty mechanisms
4. Edge case handling and numerical stability

Based on the requirements to audit scoring procedures at the meso (cluster) level
for proper handling of dispersion and convergence in policy area score averages.
"""

from __future__ import annotations

import json
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass
class ScoringScenario:
    """Test scenario for scoring analysis."""
    
    name: str
    scores: list[float]
    expected_behavior: str
    scenario_type: str  # "convergence", "dispersion", "mixed"


@dataclass
class MathematicalAuditResult:
    """Results from mathematical audit."""
    
    scenario: str
    scores: list[float]
    mean: float
    variance: float
    std_dev: float
    coefficient_variation: float
    weighted_score: float
    penalty_factor: float
    adjusted_score: float
    coherence: float
    dispersion_index: float
    mathematical_correctness: bool
    sensitivity_rating: str
    issues: list[str]
    recommendations: list[str]


class MesoScoringAuditor:
    """
    Mathematical auditor for meso-level (cluster) scoring procedures.
    
    This auditor validates:
    - Mathematical correctness of formulas
    - Appropriate sensitivity to score dispersion
    - Adaptability across different scenarios
    - Numerical stability and edge cases
    """
    
    MAX_SCORE = 3.0
    CURRENT_PENALTY_WEIGHT = 0.3  # From ClusterAggregator.PENALTY_WEIGHT
    
    def __init__(self) -> None:
        """Initialize the auditor."""
        self.audit_results: list[MathematicalAuditResult] = []
        self.severity_counts = {"CRITICAL": 0, "HIGH": 0, "MEDIUM": 0, "LOW": 0}
        
    def analyze_current_implementation(
        self,
        scores: list[float],
        weights: list[float] | None = None
    ) -> dict[str, Any]:
        """
        Analyze the current ClusterAggregator implementation.
        
        Current implementation (from aggregation.py lines 2018-2031):
        1. weighted_score = sum(score * weight for score, weight in zip(scores, weights))
        2. variance = sum((score - mean) ** 2 for score in scores) / len(scores)
        3. std_dev = variance ** 0.5
        4. normalized_std = min(std_dev / MAX_SCORE, 1.0) if std_dev > 0 else 0.0
        5. penalty_factor = 1.0 - (normalized_std * PENALTY_WEIGHT)
        6. adjusted_score = weighted_score * penalty_factor
        
        Args:
            scores: List of policy area scores [0-3]
            weights: Optional weights (default: equal weights)
            
        Returns:
            Dictionary with computed values and analysis
        """
        if not scores:
            return {
                "error": "Empty scores list",
                "mathematical_correctness": False
            }
        
        # Set equal weights if not provided
        if weights is None:
            weights = [1.0 / len(scores)] * len(scores)
        
        # Validate inputs
        if len(weights) != len(scores):
            return {
                "error": f"Weight length mismatch: {len(weights)} != {len(scores)}",
                "mathematical_correctness": False
            }
        
        if abs(sum(weights) - 1.0) > 1e-6:
            return {
                "error": f"Weights don't sum to 1.0: {sum(weights):.6f}",
                "mathematical_correctness": False
            }
        
        # Calculate weighted average
        weighted_score = sum(s * w for s, w in zip(scores, weights, strict=True))
        
        # Calculate variance (population variance, not sample)
        mean_score = sum(scores) / len(scores)
        variance = sum((s - mean_score) ** 2 for s in scores) / len(scores)
        
        # Calculate standard deviation
        std_dev = variance ** 0.5  # This is mathematically correct
        
        # Normalize standard deviation
        normalized_std = min(std_dev / self.MAX_SCORE, 1.0) if std_dev > 0 else 0.0
        
        # Apply penalty factor
        penalty_factor = 1.0 - (normalized_std * self.CURRENT_PENALTY_WEIGHT)
        
        # Calculate adjusted score
        adjusted_score = weighted_score * penalty_factor
        
        # Calculate coherence (from analyze_coherence method)
        if len(scores) <= 1:
            coherence = 1.0
        else:
            coherence = max(0.0, 1.0 - (std_dev / self.MAX_SCORE))
        
        # Calculate coefficient of variation (for dispersion analysis)
        cv = std_dev / mean_score if mean_score > 0 else 0.0
        
        # Calculate dispersion index (normalized range)
        score_range = max(scores) - min(scores) if scores else 0.0
        dispersion_index = score_range / self.MAX_SCORE
        
        return {
            "scores": scores,
            "weights": weights,
            "mean": mean_score,
            "weighted_score": weighted_score,
            "variance": variance,
            "std_dev": std_dev,
            "normalized_std": normalized_std,
            "coefficient_variation": cv,
            "dispersion_index": dispersion_index,
            "penalty_factor": penalty_factor,
            "adjusted_score": adjusted_score,
            "coherence": coherence,
            "mathematical_correctness": True
        }
    
    def evaluate_mathematical_correctness(
        self,
        analysis: dict[str, Any]
    ) -> tuple[bool, list[str]]:
        """
        Evaluate mathematical correctness of the scoring procedure.
        
        Checks:
        1. Variance calculation correctness
        2. Standard deviation calculation (should be sqrt of variance)
        3. Normalization bounds [0, 1]
        4. Penalty factor bounds [0, 1]
        5. Score bounds [0, MAX_SCORE]
        
        Returns:
            Tuple of (is_correct, list of issues)
        """
        issues = []
        
        if "error" in analysis:
            return False, [analysis["error"]]
        
        # Check variance >= 0
        if analysis["variance"] < 0:
            issues.append(f"CRITICAL: Negative variance: {analysis['variance']}")
        
        # Check std_dev = sqrt(variance)
        expected_std = analysis["variance"] ** 0.5
        if abs(analysis["std_dev"] - expected_std) > 1e-9:
            issues.append(
                f"CRITICAL: std_dev calculation error. "
                f"Expected {expected_std:.10f}, got {analysis['std_dev']:.10f}"
            )
        
        # Check normalized_std in [0, 1]
        if not (0 <= analysis["normalized_std"] <= 1.0):
            issues.append(
                f"HIGH: normalized_std out of bounds [0, 1]: {analysis['normalized_std']}"
            )
        
        # Check penalty_factor in [0, 1]
        if not (0 <= analysis["penalty_factor"] <= 1.0):
            issues.append(
                f"HIGH: penalty_factor out of bounds [0, 1]: {analysis['penalty_factor']}"
            )
        
        # Check adjusted_score in [0, MAX_SCORE]
        if not (0 <= analysis["adjusted_score"] <= self.MAX_SCORE):
            issues.append(
                f"MEDIUM: adjusted_score out of bounds [0, {self.MAX_SCORE}]: "
                f"{analysis['adjusted_score']}"
            )
        
        # Check coherence in [0, 1]
        if not (0 <= analysis["coherence"] <= 1.0):
            issues.append(
                f"HIGH: coherence out of bounds [0, 1]: {analysis['coherence']}"
            )
        
        return len(issues) == 0, issues
    
    def evaluate_dispersion_sensitivity(
        self,
        analysis: dict[str, Any],
        scenario_type: str
    ) -> tuple[str, list[str]]:
        """
        Evaluate sensitivity to dispersion vs convergence scenarios.
        
        Sensitivity levels:
        - EXCELLENT: Penalty appropriately scaled to dispersion
        - GOOD: Penalty generally appropriate but could be improved
        - FAIR: Penalty somewhat insensitive or overly aggressive
        - POOR: Penalty inappropriate for scenario
        
        Args:
            analysis: Analysis results from analyze_current_implementation
            scenario_type: "convergence", "dispersion", or "mixed"
            
        Returns:
            Tuple of (sensitivity_rating, list of recommendations)
        """
        recommendations = []
        
        cv = analysis["coefficient_variation"]
        dispersion_idx = analysis["dispersion_index"]
        penalty_factor = analysis["penalty_factor"]
        
        # Analyze based on scenario type
        if scenario_type == "convergence":
            # Low dispersion: should have minimal penalty
            if cv < 0.1 and penalty_factor < 0.95:
                recommendations.append(
                    f"Convergence scenario with CV={cv:.3f} has penalty_factor={penalty_factor:.3f}. "
                    f"Consider reducing penalty for low-dispersion cases."
                )
                rating = "FAIR"
            elif cv < 0.2 and penalty_factor < 0.90:
                recommendations.append(
                    f"Good convergence (CV={cv:.3f}) penalized to {penalty_factor:.3f}. "
                    f"Acceptable but could be more lenient."
                )
                rating = "GOOD"
            else:
                rating = "EXCELLENT"
                
        elif scenario_type == "dispersion":
            # High dispersion: should have significant penalty
            if cv > 0.5 and penalty_factor > 0.80:
                recommendations.append(
                    f"High dispersion scenario (CV={cv:.3f}) has only mild penalty "
                    f"(penalty_factor={penalty_factor:.3f}). Consider stronger penalties."
                )
                rating = "FAIR"
            elif cv > 0.3 and penalty_factor > 0.85:
                recommendations.append(
                    f"Moderate dispersion (CV={cv:.3f}) could use stronger penalty. "
                    f"Current: {penalty_factor:.3f}"
                )
                rating = "GOOD"
            else:
                rating = "EXCELLENT"
                
        else:  # mixed
            # Mixed scenario: penalty should be proportional
            expected_penalty = 1.0 - (dispersion_idx * 0.4)  # Example: 0-40% penalty range
            if abs(penalty_factor - expected_penalty) > 0.15:
                recommendations.append(
                    f"Mixed scenario: penalty_factor={penalty_factor:.3f} differs from "
                    f"expected ~{expected_penalty:.3f} based on dispersion_index={dispersion_idx:.3f}"
                )
                rating = "GOOD"
            else:
                rating = "EXCELLENT"
        
        # Check for fixed penalty weight limitation
        if cv > 0.4:
            recommendations.append(
                f"High CV={cv:.3f} detected. Current PENALTY_WEIGHT=0.3 is fixed. "
                f"Consider adaptive penalty weights based on scenario characteristics."
            )
        
        # Check for granularity
        if dispersion_idx > 0.6:
            recommendations.append(
                f"High dispersion_index={dispersion_idx:.3f} detected. "
                f"Consider non-linear penalty scaling for extreme dispersion cases."
            )
        
        return rating, recommendations
    
    def audit_scenario(
        self,
        scenario: ScoringScenario,
        weights: list[float] | None = None
    ) -> MathematicalAuditResult:
        """
        Audit a specific scoring scenario.
        
        Args:
            scenario: Test scenario to audit
            weights: Optional weights for scoring
            
        Returns:
            MathematicalAuditResult with complete analysis
        """
        print(f"\n{'='*80}")
        print(f"Auditing Scenario: {scenario.name}")
        print(f"Type: {scenario.scenario_type}")
        print(f"Scores: {scenario.scores}")
        print(f"Expected: {scenario.expected_behavior}")
        print(f"{'='*80}")
        
        # Analyze current implementation
        analysis = self.analyze_current_implementation(scenario.scores, weights)
        
        # Evaluate mathematical correctness
        is_correct, math_issues = self.evaluate_mathematical_correctness(analysis)
        
        # Evaluate dispersion sensitivity
        sensitivity_rating, recommendations = self.evaluate_dispersion_sensitivity(
            analysis, scenario.scenario_type
        )
        
        # Combine all issues
        all_issues = math_issues + [
            f"Sensitivity: {rec}" for rec in recommendations
        ]
        
        # Create result
        result = MathematicalAuditResult(
            scenario=scenario.name,
            scores=scenario.scores,
            mean=analysis.get("mean", 0.0),
            variance=analysis.get("variance", 0.0),
            std_dev=analysis.get("std_dev", 0.0),
            coefficient_variation=analysis.get("coefficient_variation", 0.0),
            weighted_score=analysis.get("weighted_score", 0.0),
            penalty_factor=analysis.get("penalty_factor", 1.0),
            adjusted_score=analysis.get("adjusted_score", 0.0),
            coherence=analysis.get("coherence", 0.0),
            dispersion_index=analysis.get("dispersion_index", 0.0),
            mathematical_correctness=is_correct,
            sensitivity_rating=sensitivity_rating,
            issues=all_issues,
            recommendations=recommendations
        )
        
        # Print detailed results
        print(f"\nMathematical Analysis:")
        print(f"  Mean: {result.mean:.4f}")
        print(f"  Variance: {result.variance:.4f}")
        print(f"  Std Dev: {result.std_dev:.4f}")
        print(f"  CV: {result.coefficient_variation:.4f}")
        print(f"  Dispersion Index: {result.dispersion_index:.4f}")
        print(f"\nScoring Results:")
        print(f"  Weighted Score: {result.weighted_score:.4f}")
        print(f"  Penalty Factor: {result.penalty_factor:.4f}")
        print(f"  Adjusted Score: {result.adjusted_score:.4f}")
        print(f"  Coherence: {result.coherence:.4f}")
        print(f"\nAudit Assessment:")
        print(f"  Mathematical Correctness: {'✓ PASS' if result.mathematical_correctness else '✗ FAIL'}")
        print(f"  Sensitivity Rating: {result.sensitivity_rating}")
        
        if result.issues:
            print(f"\nIssues Found ({len(result.issues)}):")
            for issue in result.issues:
                print(f"  - {issue}")
        
        if result.recommendations:
            print(f"\nRecommendations ({len(result.recommendations)}):")
            for rec in result.recommendations:
                print(f"  - {rec}")
        
        self.audit_results.append(result)
        return result
    
    def run_comprehensive_audit(self) -> dict[str, Any]:
        """
        Run comprehensive audit across multiple scenarios.
        
        Tests scenarios:
        1. Perfect convergence (all scores equal)
        2. Mild convergence (small variance)
        3. Moderate dispersion
        4. High dispersion
        5. Extreme dispersion (min and max scores)
        6. Mixed patterns
        7. Edge cases (single score, two scores)
        
        Returns:
            Summary report of audit results
        """
        print("\n" + "="*80)
        print("COMPREHENSIVE MATHEMATICAL AUDIT - MESO-LEVEL SCORING")
        print("="*80)
        
        scenarios = [
            # Convergence scenarios
            ScoringScenario(
                name="Perfect Convergence",
                scores=[2.5, 2.5, 2.5, 2.5],
                expected_behavior="Zero penalty, adjusted_score == weighted_score",
                scenario_type="convergence"
            ),
            ScoringScenario(
                name="Mild Convergence",
                scores=[2.3, 2.4, 2.5, 2.6],
                expected_behavior="Minimal penalty (~5-10%)",
                scenario_type="convergence"
            ),
            ScoringScenario(
                name="Good Convergence",
                scores=[2.0, 2.2, 2.3, 2.5],
                expected_behavior="Light penalty (~10-15%)",
                scenario_type="convergence"
            ),
            
            # Dispersion scenarios
            ScoringScenario(
                name="Moderate Dispersion",
                scores=[1.5, 2.0, 2.5, 3.0],
                expected_behavior="Moderate penalty (~20-30%)",
                scenario_type="dispersion"
            ),
            ScoringScenario(
                name="High Dispersion",
                scores=[0.5, 1.5, 2.5, 3.0],
                expected_behavior="Strong penalty (~30-40%)",
                scenario_type="dispersion"
            ),
            ScoringScenario(
                name="Extreme Dispersion",
                scores=[0.0, 1.0, 2.0, 3.0],
                expected_behavior="Maximum penalty (~40-50%)",
                scenario_type="dispersion"
            ),
            ScoringScenario(
                name="Bimodal Distribution",
                scores=[0.5, 0.8, 2.8, 3.0],
                expected_behavior="Strong penalty for bimodal pattern",
                scenario_type="dispersion"
            ),
            
            # Mixed scenarios
            ScoringScenario(
                name="Mixed Low-High",
                scores=[1.0, 1.5, 2.5, 3.0],
                expected_behavior="Proportional penalty to spread",
                scenario_type="mixed"
            ),
            ScoringScenario(
                name="Clustered with Outlier",
                scores=[2.0, 2.1, 2.2, 0.5],
                expected_behavior="Penalty reflects outlier impact",
                scenario_type="mixed"
            ),
            
            # Edge cases
            ScoringScenario(
                name="Single Score",
                scores=[2.5],
                expected_behavior="No penalty, perfect coherence",
                scenario_type="convergence"
            ),
            ScoringScenario(
                name="Two Identical Scores",
                scores=[2.0, 2.0],
                expected_behavior="No penalty, perfect coherence",
                scenario_type="convergence"
            ),
            ScoringScenario(
                name="Two Opposite Scores",
                scores=[0.0, 3.0],
                expected_behavior="Maximum penalty for extreme opposition",
                scenario_type="dispersion"
            ),
            
            # Real-world patterns
            ScoringScenario(
                name="Mostly Good with One Weak",
                scores=[2.5, 2.6, 2.7, 1.2],
                expected_behavior="Moderate penalty for weak area",
                scenario_type="mixed"
            ),
            ScoringScenario(
                name="Mostly Weak with One Strong",
                scores=[0.8, 1.0, 1.2, 2.8],
                expected_behavior="Penalty reflects overall weakness despite strong area",
                scenario_type="mixed"
            ),
        ]
        
        # Run all scenarios
        for scenario in scenarios:
            self.audit_scenario(scenario)
        
        # Generate summary report
        return self.generate_summary_report()
    
    def generate_summary_report(self) -> dict[str, Any]:
        """
        Generate comprehensive summary report.
        
        Returns:
            Dictionary with summary statistics and recommendations
        """
        if not self.audit_results:
            return {"error": "No audit results available"}
        
        # Calculate statistics
        total_scenarios = len(self.audit_results)
        mathematically_correct = sum(
            1 for r in self.audit_results if r.mathematical_correctness
        )
        
        # Count sensitivity ratings
        sensitivity_counts = {
            "EXCELLENT": 0,
            "GOOD": 0,
            "FAIR": 0,
            "POOR": 0
        }
        for result in self.audit_results:
            if result.sensitivity_rating in sensitivity_counts:
                sensitivity_counts[result.sensitivity_rating] += 1
        
        # Collect all unique recommendations
        all_recommendations = set()
        for result in self.audit_results:
            for rec in result.recommendations:
                # Generalize recommendations
                if "Consider adaptive penalty" in rec or "fixed" in rec.lower():
                    all_recommendations.add(
                        "Implement adaptive penalty weights based on scenario characteristics"
                    )
                elif "non-linear" in rec.lower():
                    all_recommendations.add(
                        "Implement non-linear penalty scaling for extreme dispersion cases"
                    )
                elif "reducing penalty" in rec.lower():
                    all_recommendations.add(
                        "Reduce penalties for low-dispersion convergence scenarios"
                    )
                elif "stronger penalty" in rec.lower() or "stronger penalties" in rec.lower():
                    all_recommendations.add(
                        "Strengthen penalties for high-dispersion scenarios"
                    )
        
        # Generate report
        print(f"\n{'='*80}")
        print("AUDIT SUMMARY REPORT")
        print(f"{'='*80}")
        print(f"\nTotal Scenarios Tested: {total_scenarios}")
        print(f"Mathematical Correctness: {mathematically_correct}/{total_scenarios} "
              f"({100*mathematically_correct/total_scenarios:.1f}%)")
        
        print(f"\nSensitivity Rating Distribution:")
        for rating, count in sensitivity_counts.items():
            pct = 100 * count / total_scenarios if total_scenarios > 0 else 0
            print(f"  {rating}: {count} ({pct:.1f}%)")
        
        # Calculate overall sensitivity score
        rating_scores = {"EXCELLENT": 4, "GOOD": 3, "FAIR": 2, "POOR": 1}
        avg_sensitivity = sum(
            rating_scores[r.sensitivity_rating] for r in self.audit_results
        ) / total_scenarios
        
        print(f"\nOverall Sensitivity Score: {avg_sensitivity:.2f}/4.0 "
              f"({100*avg_sensitivity/4:.1f}%)")
        
        if avg_sensitivity >= 3.5:
            overall_rating = "EXCELLENT"
        elif avg_sensitivity >= 2.5:
            overall_rating = "GOOD"
        elif avg_sensitivity >= 1.5:
            overall_rating = "FAIR"
        else:
            overall_rating = "POOR"
        
        print(f"Overall Assessment: {overall_rating}")
        
        # Print key recommendations
        if all_recommendations:
            print(f"\nKey Recommendations for Improvement:")
            for i, rec in enumerate(sorted(all_recommendations), 1):
                print(f"  {i}. {rec}")
        
        # Critical findings
        critical_issues = []
        for result in self.audit_results:
            for issue in result.issues:
                if issue.startswith("CRITICAL"):
                    critical_issues.append(f"{result.scenario}: {issue}")
        
        if critical_issues:
            print(f"\n⚠️  CRITICAL ISSUES FOUND ({len(critical_issues)}):")
            for issue in critical_issues:
                print(f"  - {issue}")
        else:
            print(f"\n✓ No critical mathematical errors found")
        
        # Create summary dict
        summary = {
            "total_scenarios": total_scenarios,
            "mathematically_correct": mathematically_correct,
            "mathematical_correctness_rate": mathematically_correct / total_scenarios,
            "sensitivity_distribution": sensitivity_counts,
            "average_sensitivity_score": avg_sensitivity,
            "overall_rating": overall_rating,
            "recommendations": list(all_recommendations),
            "critical_issues": critical_issues,
            "detailed_results": [
                {
                    "scenario": r.scenario,
                    "scores": r.scores,
                    "cv": r.coefficient_variation,
                    "dispersion_index": r.dispersion_index,
                    "penalty_factor": r.penalty_factor,
                    "adjusted_score": r.adjusted_score,
                    "mathematical_correctness": r.mathematical_correctness,
                    "sensitivity_rating": r.sensitivity_rating
                }
                for r in self.audit_results
            ]
        }
        
        return summary


def main() -> int:
    """Run the comprehensive audit."""
    auditor = MesoScoringAuditor()
    
    try:
        summary = auditor.run_comprehensive_audit()
        
        # Save detailed report to file
        output_path = Path(__file__).parent / "audit_meso_scoring_report.json"
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(summary, f, indent=2, ensure_ascii=False)
        
        print(f"\n{'='*80}")
        print(f"Detailed audit report saved to: {output_path}")
        print(f"{'='*80}\n")
        
        # Return exit code based on overall assessment
        if summary["overall_rating"] in ["EXCELLENT", "GOOD"]:
            return 0
        elif summary["overall_rating"] == "FAIR":
            return 1
        else:
            return 2
            
    except Exception as e:
        print(f"\n❌ Audit failed with error: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        return 3


if __name__ == "__main__":
    sys.exit(main())
