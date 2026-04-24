"""
Chapter models for Narrative Nexus.
"""

from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field


class ChapterBase(BaseModel):
    """Base chapter model."""
    title: str = Field(..., min_length=1, max_length=500)
    summary: Optional[str] = Field(None, max_length=2000)
    order: int = Field(..., ge=0)


class ChapterCreate(ChapterBase):
    """Model for creating a chapter."""
    story_id: str


class ChapterUpdate(BaseModel):
    """Model for updating a chapter."""
    title: Optional[str] = Field(None, min_length=1, max_length=500)
    summary: Optional[str] = Field(None, max_length=2000)
    order: Optional[int] = Field(None, ge=0)
    content: Optional[str] = None


class Chapter(ChapterBase):
    """Complete chapter model."""
    id: str
    story_id: str
    content: Optional[str] = None
    word_count: int = 0
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    scene_ids: List[str] = Field(default_factory=list)
    
    class Config:
        from_attributes = True
