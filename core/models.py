"""
core/models.py - Domain models and protocols for German B1, B2, and C1 exercises.
"""

from enum import Enum
from dataclasses import dataclass, field
from typing import Optional, List, Dict, Any, Protocol


class CEFRLevel(str, Enum):
    ALL = "All"
    A1 = "A1"
    A2 = "A2"
    B1 = "B1"
    B2 = "B2"
    C1 = "C1"
    C2 = "C2"

    @classmethod
    def from_str(cls, val: str) -> "CEFRLevel":
        v = val.strip().upper()
        for member in cls:
            if member.value == v:
                return member
        return cls.ALL


class ExerciseType(str, Enum):
    STANDARD = "standard"          # Standard front/back vocabulary or sentence
    NVR = "nvr"                    # Nomen-Verb-Verbindung (B2)
    CLOZE = "cloze"                # Fill in the missing preposition/ending (B1-C1)
    TRANSFORMATION = "transform"   # Verbalstil -> Nominalstil, Aktiv -> Passiv (B2/C1)


@dataclass
class ReviewRating:
    NEEDS_PRACTICE = 1
    GOOD = 2
    MASTERED = 3


@dataclass
class Flashcard:
    """
    Core Domain Model for a learning item.
    Supports in-line grammar, CEFR level tagging, collocations, and example sentences.
    """
    german: str
    english: str
    category: str
    level: CEFRLevel = CEFRLevel.ALL
    exercise_type: ExerciseType = ExerciseType.STANDARD
    clean_prompt: str = ""
    plural: Optional[str] = None
    grammar_note: Optional[str] = None
    example_sentence: Optional[str] = None
    collocations: List[str] = field(default_factory=list)

    def __post_init__(self):
        if not self.clean_prompt:
            from core.grammar import parse_german_grammar
            clean, pl, note = parse_german_grammar(self.german)
            self.clean_prompt = clean
            self.plural = pl
            self.grammar_note = note

    def get_article(self) -> Optional[str]:
        """Detect German grammatical article if present."""
        target = self.clean_prompt or self.german
        words = target.strip().split()
        if words:
            first = words[0].lower()
            if first in ("der", "die", "das"):
                return first
        return None

    @property
    def key(self) -> str:
        """Deterministic key for progress persistence."""
        return f"{self.category}::{self.german}"


class ExerciseItem(Protocol):
    """Protocol for polymorphic exercises across B1, B2, C1."""
    id: str
    level: CEFRLevel
    exercise_type: ExerciseType
    prompt: str
    target_answer: str

    def get_audio_text(self) -> str:
        ...
