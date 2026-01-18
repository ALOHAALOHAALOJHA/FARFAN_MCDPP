from typing import Any, List, Dict
from dataclasses import dataclass

@dataclass
class ExtractedNorm:
    id: str
    content: str

class NormativeContextManager:
    def __init__(self, municipality: str, enable_validation: bool = True):
        self.municipality = municipality

    def load_norms(self, path: str) -> List[ExtractedNorm]:
        return []

    def group_by_policy_area(self, norms: List[ExtractedNorm]) -> Dict[str, List[ExtractedNorm]]:
        return {}
