"""
Pipeline models for Narrative Nexus.
9-phase state machine for story generation.
"""

from datetime import datetime
from typing import Optional, List, Dict, Any
from enum import Enum
from pydantic import BaseModel, Field


class PipelinePhase(str, Enum):
    """Pipeline phase enumeration - 9 phases."""
    CONCEPT = "concept"
    OUTLINE = "outline"
    BEAT_SHEET = "beat_sheet"
    DRAFTING = "drafting"
    CRITIQUE = "critique"
    REWRITE = "rewrite"
    POLISH = "polish"
    CONSISTENCY = "consistency"
    EXPORT = "export"


class PipelineStatus(str, Enum):
    """Pipeline status enumeration."""
    PENDING = "pending"
    RUNNING = "running"
    WAITING_APPROVAL = "waiting_approval"
    COMPLETED = "completed"
    FAILED = "failed"
    PAUSED = "paused"


class PhaseResult(BaseModel):
    """Result from a pipeline phase."""
    phase: PipelinePhase
    status: str
    output: Dict[str, Any] = Field(default_factory=dict)
    errors: List[str] = Field(default_factory=list)
    requires_approval: bool = False
    approval_status: Optional[str] = None
    completed_at: Optional[datetime] = None


class PipelineProgress(BaseModel):
    """Pipeline progress tracking."""
    current_phase: PipelinePhase
    overall_status: PipelineStatus = PipelineStatus.PENDING
    phase_results: Dict[PipelinePhase, PhaseResult] = Field(default_factory=dict)
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    progress_percentage: float = 0.0
    current_step: Optional[str] = None
    total_steps: int = 0
    completed_steps: int = 0


class PipelineState(BaseModel):
    """Complete pipeline state."""
    id: str
    story_id: str
    status: PipelineStatus = PipelineStatus.PENDING
    current_phase: Optional[PipelinePhase] = None
    progress: PipelineProgress = Field(default_factory=lambda: PipelineProgress(
        current_phase=PipelinePhase.CONCEPT,
        overall_status=PipelineStatus.PENDING
    ))
    config: Dict[str, Any] = Field(default_factory=dict)
    metadata: Dict[str, Any] = Field(default_factory=dict)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    checkpoint_data: Optional[Dict[str, Any]] = None
    
    class Config:
        from_attributes = True
        use_enum_values = True
