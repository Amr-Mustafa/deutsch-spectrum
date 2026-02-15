from pydantic import BaseModel, Field
from typing import List, Optional


class AnalyzeRequest(BaseModel):
    """Request model for text analysis endpoint."""
    text: str = Field(..., description="German text to analyze")
    target_word: Optional[str] = Field(None, description="Specific word that was hovered")
    target_position: Optional[int] = Field(None, description="Character position of target word in text")


class VerbPreposition(BaseModel):
    """Represents a preposition associated with a verb."""
    text: str
    case: str  # e.g., "Akkusativ", "Dativ", "Akkusativ/Dativ"
    position: int  # Character position in text


class Token(BaseModel):
    """Represents a single token with its POS information."""
    text: str
    pos: str
    lemma: str
    start: int
    end: int
    is_separable: bool = False
    separable_parts: Optional[List[str]] = None
    paired_with: Optional[List[int]] = None  # Positions of all paired tokens (particles, pronouns)
    is_reflexive: bool = False
    verb_prepositions: Optional[List[VerbPreposition]] = None  # Prepositions used with this verb
    linked_verb: Optional[int] = None  # For prepositions: position of the verb they're linked to
    governs_case: Optional[str] = None  # For prepositions: the case they govern


class AnalyzeResponse(BaseModel):
    """Response model containing POS analysis results."""
    tokens: List[Token]


class POSCategory(BaseModel):
    """Represents a POS category with its color and label."""
    pos: str
    color: str
    label: str


class POSCategoriesResponse(BaseModel):
    """Response model for available POS categories."""
    categories: List[POSCategory]


class HealthResponse(BaseModel):
    """Health check response."""
    status: str
    model_loaded: bool
