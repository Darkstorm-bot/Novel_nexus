"""
Narrative Nexus - Schema Models
Pydantic v2 models for all entities.
"""

from .story import Story, StoryCreate, StoryUpdate, StoryStatus
from .chapter import Chapter, ChapterCreate, ChapterUpdate
from .scene import Scene, SceneCreate, SceneUpdate
from .character import Character, CharacterCreate, CharacterUpdate, CharacterState
from .memory import MemoryEntry, MemoryType, VectorMemory, EpisodicMemory, WorkingMemory
from .pipeline import PipelineState, PipelinePhase, PipelineProgress

__all__ = [
    "Story",
    "StoryCreate",
    "StoryUpdate",
    "StoryStatus",
    "Chapter",
    "ChapterCreate",
    "ChapterUpdate",
    "Scene",
    "SceneCreate",
    "SceneUpdate",
    "Character",
    "CharacterCreate",
    "CharacterUpdate",
    "CharacterState",
    "MemoryEntry",
    "MemoryType",
    "VectorMemory",
    "EpisodicMemory",
    "WorkingMemory",
    "PipelineState",
    "PipelinePhase",
    "PipelineProgress",
]
