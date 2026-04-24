"""
Story models for Narrative Nexus.
"""

from datetime import datetime
from enum import Enum
from typing import Optional, List
from pydantic import BaseModel, Field


class StoryStatus(str, Enum):
    """Story status enumeration."""
    DRAFT = "draft"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    ARCHIVED = "archived"


class StoryBase(BaseModel):
    """Base story model."""
    title: str = Field(..., min_length=1, max_length=500)
    description: Optional[str] = Field(None, max_length=2000)
    genre: Optional[str] = Field(None, max_length=200)
    tags: Optional[List[str]] = Field(default_factory=list)


class StoryCreate(StoryBase):
    """Model for creating a story."""
    pass


class StoryUpdate(BaseModel):
    """Model for updating a story."""
    title: Optional[str] = Field(None, min_length=1, max_length=500)
    description: Optional[str] = Field(None, max_length=2000)
    genre: Optional[str] = Field(None, max_length=200)
    tags: Optional[List[str]] = None
    status: Optional[StoryStatus] = None


class Story(StoryBase):
    """Complete story model."""
    id: str
    status: StoryStatus = StoryStatus.DRAFT
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    chapter_count: int = 0
    word_count: int = 0
    
    class Config:
        from_attributes = True
