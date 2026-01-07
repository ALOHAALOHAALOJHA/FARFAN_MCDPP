"""
FARFAN Pipeline Scorers

This module provides signal-based scorers for Phase 3 scoring.

Available Scorers:
- PolicyAreaScorer (@p): Policy Area scoring with normative compliance

Author: FARFAN Pipeline Team
Version: 1.0.0
"""

from .policy_area_scorer import (
    PolicyAreaScorer,
    PolicyAreaScore,
)

__all__ = [
    'PolicyAreaScorer',
    'PolicyAreaScore',
]
