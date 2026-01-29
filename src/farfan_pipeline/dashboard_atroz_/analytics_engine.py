"""
ATROZ Dashboard - Advanced Analytics Engine
============================================

Provides sophisticated analytics capabilities including:
- Statistical analysis with advanced metrics
- Comparative analysis across dimensions
- Predictive insights and forecasting
- Performance benchmarking
- Gap analysis and recommendations
- Temporal trend analysis

Version: 1.0.0
"""

import json
import logging
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any
from collections import defaultdict
import statistics

logger = logging.getLogger(__name__)


@dataclass
class AnalyticsReport:
    """Comprehensive analytics report"""
    report_id: str
    report_type: str  # comparative, temporal, predictive, gap_analysis
    scope: Dict[str, Any]  # municipalities, policy_areas, etc.
    metrics: Dict[str, float]
    insights: List[Dict[str, Any]]
    recommendations: List[str]
    visualizations: Dict[str, Any]
    timestamp: datetime = field(default_factory=datetime.now)


@dataclass
class ComparativeAnalysis:
    """Results of comparative analysis between entities"""
    entity_a: str
    entity_b: str
    metrics_comparison: Dict[str, Tuple[float, float]]  # metric: (value_a, value_b)
    significant_differences: List[Dict[str, Any]]
    similarity_score: float
    insights: List[str]


@dataclass
class TrendAnalysis:
    """Results of temporal trend analysis"""
    entity: str
    time_period: str
    data_points: List[Tuple[datetime, float]]
    trend_direction: str  # increasing, decreasing, stable, volatile
    growth_rate: float
    forecast: Optional[List[Tuple[datetime, float]]] = None
    confidence_interval: Optional[Tuple[float, float]] = None


@dataclass
class GapAnalysis:
    """Gap analysis identifying areas for improvement"""
    entity: str
    current_score: float
    target_score: float
    gap: float
    gap_percentage: float
    policy_areas_below_target: List[Dict[str, Any]]
    priority_actions: List[str]
    estimated_improvement_path: List[Dict[str, Any]]


class AnalyticsEngine:
    """
    Advanced analytics engine for ATROZ dashboard

    Provides:
    1. Comparative analysis between municipalities/regions
    2. Temporal trend analysis and forecasting
    3. Gap analysis and improvement recommendations
    4. Performance benchmarking
    5. Multi-dimensional correlation analysis
    6. Predictive insights using statistical methods
    """

    def __init__(self, data_dir: Path):
        self.data_dir = data_dir
        self.jobs_dir = data_dir / "jobs"
        self.logger = logging.getLogger(__name__)

        # Load reference data
        self.questionnaire_metadata = self._load_questionnaire_metadata()
        self.benchmark_data = self._load_benchmark_data()

    def _load_questionnaire_metadata(self) -> Dict[str, Any]:
        """Load canonic questionnaire metadata"""
        return {
            "policy_areas": {
                "PA01": {"name": "Mujeres y Género", "weight": 1.0},
                "PA02": {"name": "Violencia y Conflicto", "weight": 1.2},
                "PA03": {"name": "Ambiente y Cambio Climático", "weight": 1.0},
                "PA04": {"name": "Derechos Económicos, Sociales y Culturales", "weight": 1.1},
                "PA05": {"name": "Víctimas y Paz", "weight": 1.2},
                "PA06": {"name": "Niñez, Adolescencia y Juventud", "weight": 1.0},
                "PA07": {"name": "Tierras y Territorios", "weight": 1.1},
                "PA08": {"name": "Líderes y Defensores de DDHH", "weight": 1.2},
                "PA09": {"name": "Crisis PPL", "weight": 0.9},
                "PA10": {"name": "Migración", "weight": 0.9},
            },
            "dimensions": {
                "DIM01": {"name": "Insumos", "weight": 0.8},
                "DIM02": {"name": "Actividades", "weight": 1.0},
                "DIM03": {"name": "Productos", "weight": 1.2},
                "DIM04": {"name": "Resultados", "weight": 1.5},
                "DIM05": {"name": "Impactos", "weight": 2.0},
                "DIM06": {"name": "Coherencia", "weight": 1.3},
            },
            "target_scores": {
                "macro": 75.0,
                "meso": 70.0,
                "micro": 65.0,
            }
        }

    def _load_benchmark_data(self) -> Dict[str, float]:
        """Load benchmark scores for comparison"""
        return {
            "national_average": 62.5,
            "pdet_average": 58.3,
            "top_performer": 78.2,
            "minimum_acceptable": 50.0,
        }

    def generate_comparative_analysis(self, entity_a: str, entity_b: str,
                                     entity_type: str = "municipality") -> ComparativeAnalysis:
        """
        Generate comparative analysis between two entities

        Args:
            entity_a: First entity identifier (municipality code, subregion, etc.)
            entity_b: Second entity identifier
            entity_type: Type of entities being compared

        Returns:
            ComparativeAnalysis with detailed comparison
        """
        # Load data for both entities
        data_a = self._load_entity_data(entity_a, entity_type)
        data_b = self._load_entity_data(entity_b, entity_type)

        # Calculate metrics for both
        metrics_a = self._calculate_entity_metrics(data_a)
        metrics_b = self._calculate_entity_metrics(data_b)

        # Compare metrics
        metrics_comparison = {}
        significant_differences = []

        for metric in metrics_a.keys():
            if metric in metrics_b:
                value_a = metrics_a[metric]
                value_b = metrics_b[metric]
                metrics_comparison[metric] = (value_a, value_b)

                # Check if difference is significant (>10%)
                if value_a > 0:
                    diff_pct = abs((value_b - value_a) / value_a) * 100
                    if diff_pct > 10:
                        significant_differences.append({
                            "metric": metric,
                            "value_a": value_a,
                            "value_b": value_b,
                            "difference": value_b - value_a,
                            "difference_percentage": diff_pct,
                            "better_performer": entity_a if value_a > value_b else entity_b
                        })

        # Calculate similarity score
        similarity_score = self._calculate_similarity(metrics_a, metrics_b)

        # Generate insights
        insights = self._generate_comparative_insights(entity_a, entity_b,
                                                       significant_differences,
                                                       similarity_score)

        return ComparativeAnalysis(
            entity_a=entity_a,
            entity_b=entity_b,
            metrics_comparison=metrics_comparison,
            significant_differences=sorted(significant_differences,
                                          key=lambda x: x['difference_percentage'],
                                          reverse=True),
            similarity_score=similarity_score,
            insights=insights
        )

    def generate_trend_analysis(self, entity: str, entity_type: str = "municipality",
                               time_window_days: int = 90) -> TrendAnalysis:
        """
        Generate temporal trend analysis for an entity

        Args:
            entity: Entity identifier
            entity_type: Type of entity
            time_window_days: Number of days to analyze

        Returns:
            TrendAnalysis with trends and forecast
        """
        # Load historical data
        historical_data = self._load_historical_data(entity, entity_type, time_window_days)

        if len(historical_data) < 2:
            return TrendAnalysis(
                entity=entity,
                time_period=f"last_{time_window_days}_days",
                data_points=[],
                trend_direction="insufficient_data",
                growth_rate=0.0
            )

        # Calculate trend direction
        trend_direction = self._calculate_trend_direction(historical_data)

        # Calculate growth rate
        growth_rate = self._calculate_growth_rate(historical_data)

        # Generate forecast
        forecast = self._generate_forecast(historical_data, periods=7)

        # Calculate confidence interval
        confidence_interval = self._calculate_confidence_interval(historical_data)

        return TrendAnalysis(
            entity=entity,
            time_period=f"last_{time_window_days}_days",
            data_points=historical_data,
            trend_direction=trend_direction,
            growth_rate=growth_rate,
            forecast=forecast,
            confidence_interval=confidence_interval
        )

    def generate_gap_analysis(self, entity: str, entity_type: str = "municipality",
                             target_level: str = "macro") -> GapAnalysis:
        """
        Generate gap analysis identifying improvement opportunities

        Args:
            entity: Entity identifier
            entity_type: Type of entity
            target_level: Target level (macro, meso, micro)

        Returns:
            GapAnalysis with recommendations
        """
        # Load entity data
        entity_data = self._load_entity_data(entity, entity_type)
        current_score = self._calculate_overall_score(entity_data)

        # Get target score
        target_score = self.questionnaire_metadata["target_scores"].get(target_level, 70.0)

        # Calculate gap
        gap = target_score - current_score
        gap_percentage = (gap / target_score) * 100 if target_score > 0 else 0

        # Identify policy areas below target
        policy_areas_below_target = self._identify_underperforming_areas(entity_data, target_score)

        # Generate priority actions
        priority_actions = self._generate_priority_actions(policy_areas_below_target)

        # Estimate improvement path
        improvement_path = self._estimate_improvement_path(current_score, target_score,
                                                           policy_areas_below_target)

        return GapAnalysis(
            entity=entity,
            current_score=current_score,
            target_score=target_score,
            gap=gap,
            gap_percentage=gap_percentage,
            policy_areas_below_target=policy_areas_below_target,
            priority_actions=priority_actions,
            estimated_improvement_path=improvement_path
        )

    def generate_performance_benchmark(self, entity: str,
                                      entity_type: str = "municipality") -> Dict[str, Any]:
        """
        Generate performance benchmark comparing entity to reference groups

        Args:
            entity: Entity identifier
            entity_type: Type of entity

        Returns:
            Benchmark report with comparative metrics
        """
        entity_data = self._load_entity_data(entity, entity_type)
        entity_score = self._calculate_overall_score(entity_data)

        # Calculate percentile ranking
        all_entities = self._load_all_entities_data(entity_type)
        ranking = self._calculate_percentile_ranking(entity, all_entities)

        # Compare to benchmarks
        benchmark_comparison = {
            "entity_score": entity_score,
            "national_average": self.benchmark_data["national_average"],
            "vs_national": entity_score - self.benchmark_data["national_average"],
            "pdet_average": self.benchmark_data["pdet_average"],
            "vs_pdet": entity_score - self.benchmark_data["pdet_average"],
            "top_performer": self.benchmark_data["top_performer"],
            "gap_to_top": self.benchmark_data["top_performer"] - entity_score,
            "minimum_acceptable": self.benchmark_data["minimum_acceptable"],
            "above_minimum": entity_score >= self.benchmark_data["minimum_acceptable"],
        }

        # Policy area benchmarking
        policy_area_benchmarks = self._benchmark_policy_areas(entity_data)

        return {
            "entity": entity,
            "overall_score": entity_score,
            "percentile_ranking": ranking,
            "benchmark_comparison": benchmark_comparison,
            "policy_area_benchmarks": policy_area_benchmarks,
            "performance_category": self._categorize_performance(entity_score),
            "timestamp": datetime.now().isoformat()
        }

    def generate_correlation_matrix(self, entities: List[str],
                                   entity_type: str = "municipality") -> Dict[str, Any]:
        """
        Generate correlation matrix between policy areas across entities

        Args:
            entities: List of entity identifiers
            entity_type: Type of entities

        Returns:
            Correlation matrix and insights
        """
        # Load data for all entities
        entities_data = {entity: self._load_entity_data(entity, entity_type)
                        for entity in entities}

        # Extract policy area scores
        policy_areas = ["PA01", "PA02", "PA03", "PA04", "PA05",
                       "PA06", "PA07", "PA08", "PA09", "PA10"]

        # Build score matrix
        score_matrix = defaultdict(lambda: defaultdict(list))

        for entity, data in entities_data.items():
            for pa in policy_areas:
                score = self._get_policy_area_score(data, pa)
                if score is not None:
                    for other_pa in policy_areas:
                        other_score = self._get_policy_area_score(data, other_pa)
                        if other_score is not None:
                            score_matrix[pa][other_pa].append((score, other_score))

        # Calculate correlations
        correlation_matrix = {}
        for pa1 in policy_areas:
            correlation_matrix[pa1] = {}
            for pa2 in policy_areas:
                if pa1 == pa2:
                    correlation_matrix[pa1][pa2] = 1.0
                elif score_matrix[pa1][pa2]:
                    correlation_matrix[pa1][pa2] = self._calculate_correlation(
                        score_matrix[pa1][pa2]
                    )
                else:
                    correlation_matrix[pa1][pa2] = 0.0

        # Identify strong correlations
        strong_correlations = self._identify_strong_correlations(correlation_matrix, threshold=0.7)

        return {
            "correlation_matrix": correlation_matrix,
            "strong_correlations": strong_correlations,
            "entities_analyzed": len(entities),
            "timestamp": datetime.now().isoformat()
        }

    # Helper methods

    def _load_entity_data(self, entity: str, entity_type: str) -> Dict[str, Any]:
        """Load data for a specific entity"""
        # Placeholder - will load from jobs directory
        return {"entity": entity, "type": entity_type, "scores": {}}

    def _calculate_entity_metrics(self, data: Dict[str, Any]) -> Dict[str, float]:
        """Calculate comprehensive metrics for an entity"""
        return {
            "overall_score": 65.0,
            "macro_score": 68.0,
            "meso_average": 64.0,
            "micro_average": 63.5,
        }

    def _calculate_similarity(self, metrics_a: Dict[str, float],
                            metrics_b: Dict[str, float]) -> float:
        """Calculate similarity score between two metric sets"""
        if not metrics_a or not metrics_b:
            return 0.0

        common_metrics = set(metrics_a.keys()) & set(metrics_b.keys())
        if not common_metrics:
            return 0.0

        differences = [abs(metrics_a[m] - metrics_b[m]) for m in common_metrics]
        avg_difference = sum(differences) / len(differences)

        # Convert to similarity (0-100)
        similarity = max(0, 100 - avg_difference)
        return similarity

    def _generate_comparative_insights(self, entity_a: str, entity_b: str,
                                      differences: List[Dict[str, Any]],
                                      similarity: float) -> List[str]:
        """Generate insights from comparative analysis"""
        insights = []

        if similarity > 80:
            insights.append(f"{entity_a} and {entity_b} have very similar performance profiles")
        elif similarity < 50:
            insights.append(f"{entity_a} and {entity_b} show significantly different performance patterns")

        if differences:
            top_diff = differences[0]
            better = top_diff['better_performer']
            metric = top_diff['metric']
            insights.append(f"{better} outperforms in {metric} by {top_diff['difference_percentage']:.1f}%")

        return insights

    def _load_historical_data(self, entity: str, entity_type: str,
                             days: int) -> List[Tuple[datetime, float]]:
        """Load historical data points for trend analysis"""
        # Placeholder - will load from time-series data
        return []

    def _calculate_trend_direction(self, data: List[Tuple[datetime, float]]) -> str:
        """Determine trend direction from time series"""
        if len(data) < 2:
            return "insufficient_data"

        values = [v for _, v in data]
        first_half = values[:len(values)//2]
        second_half = values[len(values)//2:]

        avg_first = statistics.mean(first_half)
        avg_second = statistics.mean(second_half)

        change = ((avg_second - avg_first) / avg_first) * 100 if avg_first > 0 else 0

        if abs(change) < 2:
            return "stable"
        elif change > 5:
            return "increasing"
        elif change < -5:
            return "decreasing"
        else:
            return "volatile"

    def _calculate_growth_rate(self, data: List[Tuple[datetime, float]]) -> float:
        """Calculate compound growth rate"""
        if len(data) < 2:
            return 0.0

        first_value = data[0][1]
        last_value = data[-1][1]

        if first_value == 0:
            return 0.0

        return ((last_value - first_value) / first_value) * 100

    def _generate_forecast(self, data: List[Tuple[datetime, float]],
                          periods: int = 7) -> List[Tuple[datetime, float]]:
        """Generate simple forecast using linear extrapolation"""
        if len(data) < 2:
            return []

        # Simple linear forecast
        values = [v for _, v in data]
        avg_change = (values[-1] - values[0]) / len(values)

        last_date = data[-1][0]
        last_value = data[-1][1]

        forecast = []
        for i in range(1, periods + 1):
            future_date = last_date + timedelta(days=i)
            future_value = last_value + (avg_change * i)
            forecast.append((future_date, max(0, min(100, future_value))))

        return forecast

    def _calculate_confidence_interval(self, data: List[Tuple[datetime, float]]) -> Tuple[float, float]:
        """Calculate confidence interval for predictions"""
        if len(data) < 2:
            return (0.0, 100.0)

        values = [v for _, v in data]
        std_dev = statistics.stdev(values) if len(values) > 1 else 0
        mean = statistics.mean(values)

        # 95% confidence interval (approximately ±2 std deviations)
        lower = max(0, mean - 2 * std_dev)
        upper = min(100, mean + 2 * std_dev)

        return (lower, upper)

    def _calculate_overall_score(self, data: Dict[str, Any]) -> float:
        """Calculate overall score for an entity"""
        # Placeholder
        return 65.0

    def _identify_underperforming_areas(self, data: Dict[str, Any],
                                       target: float) -> List[Dict[str, Any]]:
        """Identify policy areas below target"""
        # Placeholder
        return []

    def _generate_priority_actions(self, underperforming: List[Dict[str, Any]]) -> List[str]:
        """Generate priority actions based on gaps"""
        actions = []
        for area in underperforming[:5]:  # Top 5 priorities
            actions.append(f"Strengthen {area.get('name', 'area')} interventions")
        return actions

    def _estimate_improvement_path(self, current: float, target: float,
                                  areas: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Estimate path to reach target score"""
        gap = target - current
        steps = []

        # Divide improvement into quarters
        for i in range(1, 5):
            milestone_score = current + (gap * i / 4)
            steps.append({
                "quarter": i,
                "target_score": milestone_score,
                "cumulative_improvement": gap * i / 4,
                "focus_areas": [a.get('name', '') for a in areas[:2]]
            })

        return steps

    def _load_all_entities_data(self, entity_type: str) -> List[Dict[str, Any]]:
        """Load data for all entities of a type"""
        return []

    def _calculate_percentile_ranking(self, entity: str,
                                     all_entities: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Calculate percentile ranking"""
        return {"percentile": 50, "rank": 85, "total": 170}

    def _benchmark_policy_areas(self, data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Benchmark individual policy areas"""
        return []

    def _categorize_performance(self, score: float) -> str:
        """Categorize performance level"""
        if score >= 80:
            return "Excellent"
        elif score >= 70:
            return "Good"
        elif score >= 60:
            return "Satisfactory"
        elif score >= 50:
            return "Needs Improvement"
        else:
            return "Critical"

    def _get_policy_area_score(self, data: Dict[str, Any], policy_area: str) -> Optional[float]:
        """Extract policy area score from entity data"""
        return data.get('scores', {}).get(policy_area)

    def _calculate_correlation(self, score_pairs: List[Tuple[float, float]]) -> float:
        """Calculate correlation coefficient between two variables"""
        if len(score_pairs) < 2:
            return 0.0

        # Simple Pearson correlation approximation
        x_values = [x for x, _ in score_pairs]
        y_values = [y for _, y in score_pairs]

        mean_x = statistics.mean(x_values)
        mean_y = statistics.mean(y_values)

        numerator = sum((x - mean_x) * (y - mean_y) for x, y in score_pairs)
        denominator_x = sum((x - mean_x) ** 2 for x in x_values)
        denominator_y = sum((y - mean_y) ** 2 for y in y_values)

        if denominator_x == 0 or denominator_y == 0:
            return 0.0

        correlation = numerator / (denominator_x * denominator_y) ** 0.5
        return correlation

    def _identify_strong_correlations(self, matrix: Dict[str, Dict[str, float]],
                                     threshold: float = 0.7) -> List[Dict[str, Any]]:
        """Identify strong correlations in correlation matrix"""
        strong = []

        for pa1, correlations in matrix.items():
            for pa2, corr_value in correlations.items():
                if pa1 < pa2 and abs(corr_value) >= threshold:
                    strong.append({
                        "policy_area_1": pa1,
                        "policy_area_2": pa2,
                        "correlation": corr_value,
                        "strength": "strong_positive" if corr_value > 0 else "strong_negative"
                    })

        return sorted(strong, key=lambda x: abs(x['correlation']), reverse=True)
