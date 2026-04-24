"""
Character models for Narrative Nexus.
"""

from datetime import datetime
from typing import Optional, List, Dict, Any
from enum import Enum
from pydantic import BaseModel, Field


class CharacterRole(str, Enum):
    """Character role enumeration."""
    PROTAGONIST = "protagonist"
    ANTAGONIST = "antagonist"
    SUPPORTING = "supporting"
    MINOR = "minor"


class CharacterState(BaseModel):
    """Character state tracking."""
    location: Optional[str] = None
    emotional_state: Optional[str] = None
    goals: List[str] = Field(default_factory=list)
    conflicts: List[str] = Field(default_factory=list)
    relationships: Dict[str, str] = Field(default_factory=dict)
    last_seen_chapter: Optional[str] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)


class CharacterBase(BaseModel):
    """Base character model."""
    name: str = Field(..., min_length=1, max_length=200)
    description: Optional[str] = Field(None, max_length=2000)
    role: CharacterRole = CharacterRole.SUPPORTING
    background: Optional[str] = Field(None, max_length=5000)
    traits: Optional[List[str]] = Field(default_factory=list)
    motivations: Optional[List[str]] = Field(default_factory=list)


class CharacterCreate(CharacterBase):
    """Model for creating a character."""
    story_id: str


class CharacterUpdate(BaseModel):
    """Model for updating a character."""
    name: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = Field(None, max_length=2000)
    role: Optional[CharacterRole] = None
    background: Optional[str] = Field(None, max_length=5000)
    traits: Optional[List[str]] = None
    motivations: Optional[List[str]] = None
    state: Optional[CharacterState] = None


class Character(CharacterBase):
    """Complete character model."""
    id: str
    story_id: str
    state: CharacterState = Field(default_factory=CharacterState)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    appearance_count: int = 0
    
    class Config:
        from_attributes = True
