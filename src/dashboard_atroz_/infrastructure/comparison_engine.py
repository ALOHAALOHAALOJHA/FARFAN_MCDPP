"""
Comparison Engine
Logic for calculating deltas and aggregating stats across regions.
"""
from typing import List, Dict, Any

class ComparisonEngine:
    def __init__(self, db_session=None):
        self.db = db_session

    def compare_regions(self, region_ids: List[str]) -> Dict[str, Any]:
        """
        Compare a list of regions.
        Returns a dictionary with 'matrix' and 'deltas'.
        """
        # In a real implementation, query the DB for these regions' scores
        # scores = self.db.query(...)

        # Mock scores for functionality
        scores = {rid: 50.0 + (i * 5.5) for i, rid in enumerate(region_ids)}

        matrix = {rid: {"overall_score": s, "rank": i+1} for rid, s in scores.items()}

        deltas = {}
        if len(region_ids) >= 2:
            r1, r2 = region_ids[0], region_ids[1]
            diff = scores[r1] - scores[r2]
            deltas[f"{r1}_vs_{r2}"] = {
                "diff": round(diff, 2),
                "leader": r1 if diff > 0 else r2
            }

        return {
            "matrix": matrix,
            "deltas": deltas,
            "metadata": {"count": len(region_ids)}
        }

    def compute_pdet_average(self, subregion_id: str) -> Dict[str, float]:
        """
        Compute average scores for a PDET subregion.
        Should use cached aggregates if available.
        """
        # Placeholder for aggregation query
        return {"overall_average": 65.4, "sample_size": 12}
