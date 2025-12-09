"""Stub for uncertainty_quantification to allow imports."""

from dataclasses import dataclass
from typing import Any

@dataclass
class UncertaintyMetrics:
    mean: float
    std: float
    confidence_interval_95: tuple[float, float]
    epistemic_uncertainty: float = 0.0
    aleatoric_uncertainty: float = 0.0
    
    def to_dict(self):
        return {
            'mean': self.mean,
            'std': self.std,
            'confidence_interval_95': self.confidence_interval_95,
            'epistemic_uncertainty': self.epistemic_uncertainty,
            'aleatoric_uncertainty': self.aleatoric_uncertainty,
        }

class BootstrapAggregator:
    def __init__(self, n_samples=1000, random_seed=42):
        pass

def aggregate_with_uncertainty(scores, weights=None, n_bootstrap=1000, random_seed=42):
    mean = sum(scores) / len(scores) if scores else 0.0
    return mean, UncertaintyMetrics(
        mean=mean,
        std=0.0,
        confidence_interval_95=(mean, mean),
        epistemic_uncertainty=0.0,
        aleatoric_uncertainty=0.0
    )
