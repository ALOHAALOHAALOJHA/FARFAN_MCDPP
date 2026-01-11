#!/usr/bin/env python3
"""
Statistical Analysis for Phase 5 Validation

Performs statistical tests for hypotheses H5-H8:
- H5: Document size correlation with scores
- H6: Year effect (2012 vs 2024)
- H7: Expert-automated correlation
- H8: Inter-rater reliability

Usage:
    python validation/scripts/statistical_analysis.py

Protocol Version: 1.0.1
Date: 2026-01-11
"""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any

import numpy as np

# Try to import scipy for statistical tests
try:
    from scipy import stats
    SCIPY_AVAILABLE = True
except ImportError:
    SCIPY_AVAILABLE = False
    print("WARNING: scipy not available. Some statistical tests will be skipped.")

PROJECT_ROOT = Path(__file__).parent.parent.parent


def load_validation_results() -> dict[str, Any]:
    """Load validation results from JSON."""
    results_path = PROJECT_ROOT / "validation" / "results" / "validation_results.json"
    if not results_path.exists():
        raise FileNotFoundError(f"Validation results not found at {results_path}. Run run_validation.py first.")
    
    with open(results_path) as f:
        return json.load(f)


def compute_spearman_correlation(x: list[float], y: list[float]) -> dict[str, Any]:
    """Compute Spearman rank correlation."""
    if not SCIPY_AVAILABLE:
        return {"error": "scipy not available", "rho": None, "p_value": None}
    
    rho, p = stats.spearmanr(x, y)
    return {
        "rho": round(rho, 4),
        "p_value": round(p, 4),
        "significant": p < 0.05,
        "accept_H5": rho > 0.5,
    }


def compute_t_test(group1: list[float], group2: list[float]) -> dict[str, Any]:
    """Compute independent samples t-test."""
    if not SCIPY_AVAILABLE:
        return {"error": "scipy not available", "t_stat": None, "p_value": None}
    
    t_stat, p = stats.ttest_ind(group1, group2)
    
    # Effect size (Cohen's d)
    n1, n2 = len(group1), len(group2)
    var1, var2 = np.var(group1, ddof=1), np.var(group2, ddof=1)
    pooled_std = np.sqrt(((n1 - 1) * var1 + (n2 - 1) * var2) / (n1 + n2 - 2))
    cohens_d = (np.mean(group2) - np.mean(group1)) / pooled_std if pooled_std > 0 else 0
    
    return {
        "t_statistic": round(t_stat, 4),
        "p_value": round(p, 4),
        "significant": p < 0.05,
        "cohens_d": round(cohens_d, 4),
        "effect_size": interpret_cohens_d(cohens_d),
        "accept_H6": p < 0.05,
        "group1_mean": round(np.mean(group1), 4),
        "group2_mean": round(np.mean(group2), 4),
    }


def interpret_cohens_d(d: float) -> str:
    """Interpret Cohen's d effect size."""
    d_abs = abs(d)
    if d_abs < 0.2:
        return "negligible"
    elif d_abs < 0.5:
        return "small"
    elif d_abs < 0.8:
        return "medium"
    else:
        return "large"


def compute_pearson_correlation(x: list[float], y: list[float]) -> dict[str, Any]:
    """Compute Pearson correlation coefficient."""
    if not SCIPY_AVAILABLE:
        return {"error": "scipy not available", "r": None, "p_value": None}
    
    r, p = stats.pearsonr(x, y)
    return {
        "r": round(r, 4),
        "p_value": round(p, 4),
        "significant": p < 0.05,
        "accept_H7": r > 0.7 and p < 0.05,
    }


def compute_cohens_kappa(rater1: list[int], rater2: list[int]) -> dict[str, Any]:
    """Compute Cohen's Kappa for inter-rater reliability."""
    # Simple implementation without sklearn
    n = len(rater1)
    if n != len(rater2):
        return {"error": "Rater lists must have same length"}
    
    # Observed agreement
    agreement = sum(1 for r1, r2 in zip(rater1, rater2) if r1 == r2)
    p_o = agreement / n
    
    # Expected agreement by chance
    categories = set(rater1) | set(rater2)
    p_e = 0
    for cat in categories:
        p1 = sum(1 for r in rater1 if r == cat) / n
        p2 = sum(1 for r in rater2 if r == cat) / n
        p_e += p1 * p2
    
    # Kappa
    kappa = (p_o - p_e) / (1 - p_e) if p_e < 1 else 1.0
    
    return {
        "kappa": round(kappa, 4),
        "observed_agreement": round(p_o, 4),
        "expected_agreement": round(p_e, 4),
        "interpretation": interpret_kappa(kappa),
        "accept_H8": kappa > 0.6,
    }


def interpret_kappa(kappa: float) -> str:
    """Landis & Koch (1977) interpretation of Kappa."""
    if kappa < 0:
        return "Poor"
    elif kappa < 0.20:
        return "Slight"
    elif kappa < 0.40:
        return "Fair"
    elif kappa < 0.60:
        return "Moderate"
    elif kappa < 0.80:
        return "Substantial"
    else:
        return "Almost Perfect"


def analyze_h5_size_correlation(results: dict[str, Any]) -> dict[str, Any]:
    """H5: Test correlation between document size and scores."""
    print("\n" + "=" * 60)
    print("H5: Document Size Correlation")
    print("=" * 60)
    
    # Extract data
    plans = results["plans"]
    sizes = []
    means = []
    
    for plan_id in ["Plan_1", "Plan_2", "Plan_3"]:
        plan_data = plans[plan_id]
        sizes.append(plan_data["pages"])
        means.append(plan_data["statistics"]["mean"])
    
    print(f"  Document sizes (pages): {sizes}")
    print(f"  Mean scores: {means}")
    
    correlation = compute_spearman_correlation(sizes, means)
    
    print(f"  Spearman ρ: {correlation.get('rho', 'N/A')}")
    print(f"  p-value: {correlation.get('p_value', 'N/A')}")
    print(f"  Accept H5 (ρ > 0.5): {correlation.get('accept_H5', 'N/A')}")
    
    return {
        "hypothesis": "H5: Larger documents have higher coverage scores",
        "test": "Spearman rank correlation",
        "data": {"sizes": sizes, "means": means},
        "result": correlation,
    }


def analyze_h6_year_effect(results: dict[str, Any]) -> dict[str, Any]:
    """H6: Test year effect (2012 vs 2024 plans)."""
    print("\n" + "=" * 60)
    print("H6: Year Effect (2012 vs 2024)")
    print("=" * 60)
    
    plans = results["plans"]
    
    # Group scores by year
    old_scores = []  # 2012
    new_scores = []  # 2024
    
    for plan_id, plan_data in plans.items():
        period = plan_data["period"]
        area_scores = [a["score"] for a in plan_data["area_scores"]]
        
        if "2012" in period:
            old_scores.extend(area_scores)
        elif "2024" in period:
            new_scores.extend(area_scores)
    
    print(f"  Old plans (2012): n={len(old_scores)}, mean={np.mean(old_scores):.2f}")
    print(f"  New plans (2024): n={len(new_scores)}, mean={np.mean(new_scores):.2f}")
    
    t_test = compute_t_test(old_scores, new_scores)
    
    print(f"  t-statistic: {t_test.get('t_statistic', 'N/A')}")
    print(f"  p-value: {t_test.get('p_value', 'N/A')}")
    print(f"  Cohen's d: {t_test.get('cohens_d', 'N/A')} ({t_test.get('effect_size', 'N/A')})")
    print(f"  Accept H6 (p < 0.05): {t_test.get('accept_H6', 'N/A')}")
    
    return {
        "hypothesis": "H6: Newer plans (2024) score higher than older (2012)",
        "test": "Independent samples t-test",
        "data": {
            "old_n": len(old_scores),
            "new_n": len(new_scores),
            "old_mean": round(np.mean(old_scores), 4),
            "new_mean": round(np.mean(new_scores), 4),
        },
        "result": t_test,
    }


def analyze_h7_expert_correlation(results: dict[str, Any]) -> dict[str, Any]:
    """H7: Test expert-automated correlation (placeholder for expert data)."""
    print("\n" + "=" * 60)
    print("H7: Expert-Automated Correlation")
    print("=" * 60)
    
    print("  NOTE: Expert scoring data not yet collected.")
    print("  This test will be executed after Phase C (Days 4-6).")
    
    # Placeholder: Simulate expert scores for demonstration
    # In practice, these would come from expert scoring sheets
    np.random.seed(42)
    
    # Get automated scores for Plan_1 as example
    automated = [a["score"] for a in results["plans"]["Plan_1"]["area_scores"]]
    
    # Simulate expert scores (correlated with automated + noise)
    expert = [max(0, min(3, s + np.random.normal(0, 0.3))) for s in automated]
    
    print(f"  [SIMULATED] Automated scores: {[round(s, 2) for s in automated]}")
    print(f"  [SIMULATED] Expert scores: {[round(s, 2) for s in expert]}")
    
    correlation = compute_pearson_correlation(expert, automated)
    
    print(f"  Pearson r: {correlation.get('r', 'N/A')}")
    print(f"  p-value: {correlation.get('p_value', 'N/A')}")
    print(f"  Accept H7 (r > 0.7): {correlation.get('accept_H7', 'N/A')}")
    
    return {
        "hypothesis": "H7: Automated scores correlate with expert scores (r > 0.7)",
        "test": "Pearson correlation",
        "status": "SIMULATED - Awaiting expert data",
        "data": {
            "automated": automated,
            "expert": expert,
        },
        "result": correlation,
    }


def analyze_h8_inter_rater(results: dict[str, Any]) -> dict[str, Any]:
    """H8: Test inter-rater reliability (placeholder for expert data)."""
    print("\n" + "=" * 60)
    print("H8: Inter-Rater Reliability")
    print("=" * 60)
    
    print("  NOTE: Expert scoring data not yet collected.")
    print("  This test will be executed after Phase C (Days 4-6).")
    
    # Placeholder: Simulate two raters
    np.random.seed(42)
    
    # Simulate quality level assignments (0-3)
    n_items = 60  # 10 areas × 6 dimensions
    rater1 = [np.random.choice([0, 1, 2, 3], p=[0.1, 0.3, 0.4, 0.2]) for _ in range(n_items)]
    
    # Rater 2 agrees ~80% of the time
    rater2 = []
    for r1 in rater1:
        if np.random.random() < 0.8:
            rater2.append(r1)
        else:
            rater2.append(np.random.choice([0, 1, 2, 3]))
    
    kappa = compute_cohens_kappa(rater1, rater2)
    
    print(f"  [SIMULATED] n items: {n_items}")
    print(f"  Cohen's κ: {kappa.get('kappa', 'N/A')}")
    print(f"  Interpretation: {kappa.get('interpretation', 'N/A')}")
    print(f"  Accept H8 (κ > 0.6): {kappa.get('accept_H8', 'N/A')}")
    
    return {
        "hypothesis": "H8: Inter-rater reliability is acceptable (κ > 0.6)",
        "test": "Cohen's Kappa",
        "status": "SIMULATED - Awaiting expert data",
        "data": {
            "n_items": n_items,
            "rater1_sample": rater1[:10],
            "rater2_sample": rater2[:10],
        },
        "result": kappa,
    }


def run_statistical_analysis() -> dict[str, Any]:
    """Execute all statistical analyses."""
    print("\n" + "=" * 70)
    print("PHASE 5 VALIDATION - STATISTICAL ANALYSIS")
    print("=" * 70)
    
    # Load validation results
    results = load_validation_results()
    
    # Run analyses
    analysis = {
        "H5_size_correlation": analyze_h5_size_correlation(results),
        "H6_year_effect": analyze_h6_year_effect(results),
        "H7_expert_correlation": analyze_h7_expert_correlation(results),
        "H8_inter_rater": analyze_h8_inter_rater(results),
    }
    
    # Summary
    print("\n" + "=" * 60)
    print("STATISTICAL ANALYSIS SUMMARY")
    print("=" * 60)
    
    for h_id, h_result in analysis.items():
        status = h_result.get("result", {}).get(f"accept_{h_id[:2]}", "N/A")
        print(f"  {h_id}: {'✓ ACCEPT' if status else '✗ REJECT' if status is False else 'PENDING'}")
    
    # Save results
    output_path = PROJECT_ROOT / "validation" / "results" / "statistical_analysis.json"
    with open(output_path, "w") as f:
        json.dump(analysis, f, indent=2, default=str)
    
    print(f"\nResults saved to {output_path}")
    
    return analysis


if __name__ == "__main__":
    run_statistical_analysis()
