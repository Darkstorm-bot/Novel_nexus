"""
Scene models for Narrative Nexus.
"""

from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field


class SceneBase(BaseModel):
    """Base scene model."""
    title: Optional[str] = Field(None, max_length=500)
    summary: Optional[str] = Field(None, max_length=2000)
    order: int = Field(..., ge=0)
    location: Optional[str] = Field(None, max_length=200)
    pov_character: Optional[str] = Field(None, max_length=200)


class SceneCreate(SceneBase):
    """Model for creating a scene."""
    chapter_id: str


class SceneUpdate(BaseModel):
    """Model for updating a scene."""
    title: Optional[str] = Field(None, max_length=500)
    summary: Optional[str] = Field(None, max_length=2000)
    order: Optional[int] = Field(None, ge=0)
    location: Optional[str] = Field(None, max_length=200)
    pov_character: Optional[str] = Field(None, max_length=200)
    content: Optional[str] = None


class Scene(SceneBase):
    """Complete scene model."""
    id: str
    chapter_id: str
    content: Optional[str] = None
    word_count: int = 0
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    character_ids: List[str] = Field(default_factory=list)
    
    class Config:
        from_attributes = True
