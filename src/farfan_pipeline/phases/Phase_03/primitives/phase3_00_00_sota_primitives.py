"""Phase 3 SOTA Primitives - Frontier Machine Learning Components

This module defines advanced mathematical primitives for state-of-the-art
signal enrichment using machine learning techniques.

Author: F.A.R.F.A.N Core Team - SOTA Division
Version: 2.0.0-SOTA
"""

from dataclasses import dataclass, field
from typing import Any
import numpy as np


@dataclass
class BayesianPosterior:
    """Represents a Bayesian posterior distribution for confidence estimation.
    
    Uses Beta distribution as conjugate prior for Binomial likelihood.
    
    Attributes:
        alpha: Success count + prior_alpha (Beta parameter)
        beta: Failure count + prior_beta (Beta parameter)
        observations: Total number of observations
    """
    alpha: float = 2.0
    beta: float = 2.0
    observations: int = 0
    
    def expected_value(self) -> float:
        """Posterior mean: E[θ] = α / (α + β)"""
        return self.alpha / (self.alpha + self.beta)
    
    def variance(self) -> float:
        """Posterior variance: Var[θ] = αβ / ((α+β)²(α+β+1))"""
        a, b = self.alpha, self.beta
        return (a * b) / ((a + b) ** 2 * (a + b + 1))
    
    def credible_interval(self, level: float = 0.95) -> tuple[float, float]:
        """Compute Bayesian credible interval."""
        try:
            from scipy.stats import beta as beta_dist
            lower = beta_dist.ppf((1 - level) / 2, self.alpha, self.beta)
            upper = beta_dist.ppf((1 + level) / 2, self.alpha, self.beta)
            return (lower, upper)
        except ImportError:
            # Fallback to approximate credible interval
            mean = self.expected_value()
            std = self.variance() ** 0.5
            return (max(0.0, mean - 1.96 * std), min(1.0, mean + 1.96 * std))


@dataclass
class AttentionWeights:
    """Represents learned attention weights for signal pattern detection.
    
    Uses scaled dot-product attention mechanism.
    
    Attributes:
        query_weights: Query projection weights (d_model × d_k)
        key_weights: Key projection weights (d_model × d_k)
        value_weights: Value projection weights (d_model × d_v)
        d_model: Model dimension
        d_k: Key/query dimension
        d_v: Value dimension
    """
    query_weights: np.ndarray = field(default_factory=lambda: np.eye(64))
    key_weights: np.ndarray = field(default_factory=lambda: np.eye(64))
    value_weights: np.ndarray = field(default_factory=lambda: np.eye(64))
    d_model: int = 64
    d_k: int = 64
    d_v: int = 64
    
    def compute_attention_scores(
        self,
        query: np.ndarray,
        keys: np.ndarray
    ) -> np.ndarray:
        """Compute scaled dot-product attention scores.
        
        Attention(Q, K) = softmax(QK^T / sqrt(d_k))
        
        Args:
            query: Query vector (d_model,)
            keys: Key matrix (n_keys, d_model)
            
        Returns:
            Attention scores (n_keys,)
        """
        # Project query and keys
        q = query @ self.query_weights  # (d_k,)
        k = keys @ self.key_weights     # (n_keys, d_k)
        
        # Scaled dot-product
        scores = (q @ k.T) / np.sqrt(self.d_k)  # (n_keys,)
        
        # Softmax
        exp_scores = np.exp(scores - np.max(scores))  # Numerical stability
        return exp_scores / exp_scores.sum()


@dataclass
class AdaGradState:
    """State for AdaGrad optimizer (adaptive gradient descent).
    
    Maintains accumulated squared gradients for adaptive learning rates.
    
    Attributes:
        grad_sum_squares: Accumulated squared gradients per parameter
        learning_rate: Base learning rate
        epsilon: Small constant for numerical stability
    """
    grad_sum_squares: dict[str, float] = field(default_factory=dict)
    learning_rate: float = 0.01
    epsilon: float = 1e-8
    
    def compute_adaptive_lr(self, param_name: str, gradient: float) -> float:
        """Compute adaptive learning rate for parameter.
        
        lr_t = lr / sqrt(Σ g_i² + ε)
        
        Args:
            param_name: Parameter identifier
            gradient: Current gradient value
            
        Returns:
            Adaptive learning rate
        """
        if param_name not in self.grad_sum_squares:
            self.grad_sum_squares[param_name] = 0.0
        
        self.grad_sum_squares[param_name] += gradient ** 2
        return self.learning_rate / np.sqrt(
            self.grad_sum_squares[param_name] + self.epsilon
        )


@dataclass
class KalmanState:
    """State for discrete Kalman filter.
    
    Represents current estimate and error covariance for optimal
    recursive estimation under Gaussian noise.
    
    Attributes:
        x: State estimate (signal freshness in [0, 1])
        P: Error covariance (uncertainty in estimate)
        Q: Process noise covariance
        R: Measurement noise covariance
    """
    x: float = 1.0  # Initial freshness
    P: float = 1.0  # Initial uncertainty
    Q: float = 0.01  # Process noise
    R: float = 0.1   # Measurement noise
    
    def predict(self, dt: float, decay_rate: float = 0.05) -> None:
        """Kalman prediction step.
        
        x̂_k|k-1 = F_k x̂_k-1|k-1
        P_k|k-1 = F_k P_k-1|k-1 F_k^T + Q_k
        
        Args:
            dt: Time step (days)
            decay_rate: Exponential decay constant
        """
        # State transition: exponential decay
        F = 1.0 - decay_rate * dt
        self.x = F * self.x
        self.P = F * self.P * F + self.Q * dt
    
    def update(self, measurement: float) -> None:
        """Kalman update step.
        
        K_k = P_k|k-1 H_k^T (H_k P_k|k-1 H_k^T + R_k)^-1
        x̂_k|k = x̂_k|k-1 + K_k (z_k - H_k x̂_k|k-1)
        P_k|k = (I - K_k H_k) P_k|k-1
        
        Args:
            measurement: Observed freshness value
        """
        # Measurement model: H = 1 (direct observation)
        H = 1.0
        
        # Kalman gain
        K = self.P * H / (H * self.P * H + self.R)
        
        # Update estimate
        innovation = measurement - H * self.x
        self.x = self.x + K * innovation
        
        # Update covariance
        self.P = (1 - K * H) * self.P
    
    def get_estimate_with_uncertainty(self) -> tuple[float, float]:
        """Get current estimate and uncertainty.
        
        Returns:
            Tuple of (estimate, std_dev)
        """
        return (self.x, np.sqrt(self.P))


@dataclass
class ProbabilisticQualityDistribution:
    """Represents probabilistic distribution over quality levels.
    
    Uses Bayesian inference to compute posterior over quality levels
    given score, completeness, and signal evidence.
    
    Attributes:
        probabilities: Probability mass for each quality level
        quality_levels: Quality level names
    """
    probabilities: dict[str, float] = field(default_factory=dict)
    quality_levels: list[str] = field(default_factory=lambda: [
        "EXCELENTE", "ACEPTABLE", "INSUFICIENTE", "NO_APLICABLE"
    ])
    
    def __post_init__(self):
        """Initialize uniform prior if no probabilities given."""
        if not self.probabilities:
            uniform_prob = 1.0 / len(self.quality_levels)
            self.probabilities = {
                level: uniform_prob for level in self.quality_levels
            }
    
    def update_with_evidence(
        self,
        score: float,
        completeness: str,
        signal_strength: float
    ) -> None:
        """Update posterior distribution given evidence.
        
        P(quality | evidence) ∝ P(evidence | quality) × P(quality)
        
        Args:
            score: Numeric score [0, 1]
            completeness: Completeness indicator
            signal_strength: Aggregated signal strength
        """
        # Likelihood: P(score | quality)
        likelihoods = {
            "EXCELENTE": self._score_likelihood(score, 0.85, 0.1),
            "ACEPTABLE": self._score_likelihood(score, 0.6, 0.15),
            "INSUFICIENTE": self._score_likelihood(score, 0.3, 0.15),
            "NO_APLICABLE": 0.1,  # Low prior
        }
        
        # Update with completeness evidence
        if completeness == "complete":
            likelihoods["EXCELENTE"] *= 2.0
            likelihoods["ACEPTABLE"] *= 1.5
        elif completeness == "insufficient":
            likelihoods["INSUFICIENTE"] *= 2.0
        
        # Update with signal strength
        for quality in likelihoods:
            likelihoods[quality] *= (1.0 + signal_strength)
        
        # Compute posterior (Bayes' rule)
        for quality in self.quality_levels:
            self.probabilities[quality] *= likelihoods[quality]
        
        # Normalize
        total = sum(self.probabilities.values())
        if total > 0:
            for quality in self.quality_levels:
                self.probabilities[quality] /= total
    
    def _score_likelihood(
        self,
        score: float,
        mean: float,
        std: float
    ) -> float:
        """Gaussian likelihood: P(score | quality with mean, std)."""
        return np.exp(-0.5 * ((score - mean) / std) ** 2)
    
    def max_posterior(self) -> str:
        """Get quality level with maximum posterior probability."""
        return max(self.probabilities.items(), key=lambda x: x[1])[0]
    
    def entropy(self) -> float:
        """Compute Shannon entropy of distribution (uncertainty measure)."""
        return -sum(
            p * np.log2(p) for p in self.probabilities.values() if p > 0
        )


# Export all SOTA primitives
__all__ = [
    "BayesianPosterior",
    "AttentionWeights",
    "AdaGradState",
    "KalmanState",
    "ProbabilisticQualityDistribution",
]
