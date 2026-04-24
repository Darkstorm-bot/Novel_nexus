"""
Memory system models for Narrative Nexus.
Three-layer memory: Vector, Episodic, and Working Memory.
"""

from datetime import datetime
from typing import Optional, List, Dict, Any
from enum import Enum
from pydantic import BaseModel, Field


class MemoryType(str, Enum):
    """Memory type enumeration."""
    VECTOR = "vector"
    EPISODIC = "episodic"
    WORKING = "working"
    CHARACTER = "character"
    PLOT = "plot"
    WORLD_BUILDING = "world_building"


class MemoryEntry(BaseModel):
    """Base memory entry model."""
    id: str
    type: MemoryType
    content: str
    metadata: Dict[str, Any] = Field(default_factory=dict)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    story_id: Optional[str] = None
    importance: float = Field(0.5, ge=0.0, le=1.0)


class VectorMemory(MemoryEntry):
    """Vector memory with embedding information."""
    type: MemoryType = MemoryType.VECTOR
    embedding_model: Optional[str] = None
    similarity_score: Optional[float] = None
    vector_id: Optional[str] = None


class EpisodicMemory(MemoryEntry):
    """Episodic memory for specific events."""
    type: MemoryType = MemoryType.EPISODIC
    event_type: Optional[str] = None
    chapter_id: Optional[str] = None
    scene_id: Optional[str] = None
    participants: List[str] = Field(default_factory=list)
    timestamp: Optional[datetime] = None


class WorkingMemory(BaseModel):
    """Working memory for active context."""
    id: str
    story_id: str
    active_characters: List[str] = Field(default_factory=list)
    current_plot_threads: List[str] = Field(default_factory=list)
    recent_events: List[str] = Field(default_factory=list)
    open_questions: List[str] = Field(default_factory=list)
    context_window: Dict[str, Any] = Field(default_factory=dict)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    class Config:
        from_attributes = True
