from dataclasses import dataclass

@dataclass(frozen=True)
class ValueAddResult:
    is_valid: bool
    empirical_availability: float
    score: float
    is_enrichment: bool
    threshold: float
    message: str

class ValueAddGate:
    """
    Gate 2: Validates value add based on empirical availability threshold.
    PATTERN: Threshold-Based Validation
    """
    EMPIRICAL_THRESHOLD: float = 0.30

    def calculate_value_score(self, empirical_availability: float) -> float:
        """Calculates value score from empirical availability."""
        if empirical_availability < 0.0:
            return 0.0
        if empirical_availability > 1.0:
            return 1.0
        return empirical_availability

    def validate(self, empirical_availability: float, is_enrichment: bool) -> ValueAddResult:
        """
        Validates if the signal provides sufficient value.
        """
        score = self.calculate_value_score(empirical_availability)
        is_valid = score >= self.EMPIRICAL_THRESHOLD
        
        msg = "Value sufficient" if is_valid else f"Value {score:.2f} below threshold {self.EMPIRICAL_THRESHOLD}"
        
        return ValueAddResult(
            is_valid=is_valid,
            empirical_availability=empirical_availability,
            score=score,
            is_enrichment=is_enrichment,
            threshold=self.EMPIRICAL_THRESHOLD,
            message=msg
        )
