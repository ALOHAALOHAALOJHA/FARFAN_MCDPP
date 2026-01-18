from typing import Any, Optional, List, Dict
from pathlib import Path
from dataclasses import dataclass, field
import json
import logging

from canonic_questionnaire_central import CQCLoader, CQCConfig

# Logger
logger = logging.getLogger(__name__)

@dataclass
class QuestionnaireMonolith:
    """Represents the loaded questionnaire monolith."""
    data: Dict[str, Any]
    policy_areas: List[Any] = field(default_factory=list)
    questions: List[Any] = field(default_factory=list)
    
    def __post_init__(self):
        # Basic parsing to populate fields if data is provided
        if self.data:
            self.policy_areas = [
                PAWrapper(pa) for pa in self.data.get("policy_areas", [])
            ]
            # Flatten questions
            self.questions = []
            for pa in self.policy_areas:
                for dim in pa.dimensions:
                    for slot in dim.slots:
                        self.questions.extend(slot.questions)

@dataclass
class PAWrapper:
    data: Dict[str, Any]
    dimensions: List[Any] = field(default_factory=list)
    
    def __post_init__(self):
        self.dimensions = [
            DimWrapper(d) for d in self.data.get("dimensions", [])
        ]
        self.id = self.data.get("id")

@dataclass
class DimWrapper:
    data: Dict[str, Any]
    slots: List[Any] = field(default_factory=list)
    
    def __post_init__(self):
        self.slots = [
            SlotWrapper(s) for s in self.data.get("slots", [])
        ]
        self.id = self.data.get("id")

@dataclass
class SlotWrapper:
    data: Dict[str, Any]
    questions: List[Any] = field(default_factory=list)
    
    def __post_init__(self):
        self.questions = [
            QWrapper(q) for q in self.data.get("questions", [])
        ]

@dataclass
class QWrapper:
    data: Dict[str, Any]
    id: str = ""
    
    def __post_init__(self):
        self.id = self.data.get("id")
        self.data_dict = self.data
    
    def to_dict(self):
        return self.data_dict

class QuestionnaireCentral:
    """
    Central access point for the questionnaire.
    Wraps CQC loader or direct file loading.
    """
    
    def __init__(
        self, 
        monolith_path: str,
        enable_validation: bool = True,
        enable_caching: bool = True
    ):
        self.monolith_path = Path(monolith_path)
        self.enable_validation = enable_validation
        self.enable_caching = enable_caching
        self.loader = CQCLoader(CQCConfig(
            registry_path=self.monolith_path.parent if self.monolith_path.exists() else None
        ))

    def load_monolith(self) -> QuestionnaireMonolith:
        """Load the full questionnaire monolith."""
        if self.monolith_path.exists():
            try:
                with open(self.monolith_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                return QuestionnaireMonolith(data=data)
            except Exception as e:
                logger.error(f"Failed to load monolith from {self.monolith_path}: {e}")
                # Fallback to CQC loader construction if file fails or is partial
                pass
        
        # If file doesn't exist or failed, return empty or constructed
        return QuestionnaireMonolith(data={})

class QuestionnaireProvider:
    """Provides questionnaire data to other components."""
    
    def __init__(self, monolith: QuestionnaireMonolith, enable_caching: bool = True):
        self.monolith = monolith
        self.enable_caching = enable_caching
    
    def get_question(self, question_id: str) -> Optional[Any]:
        for q in self.monolith.questions:
            if q.id == question_id:
                return q
        return None
