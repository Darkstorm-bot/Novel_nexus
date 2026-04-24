"""
Pipeline State Machine - 9-phase story generation workflow.
Uses transitions library for state management.
"""

from typing import Optional, Dict, Any, Callable, List
from datetime import datetime
import uuid

from transitions import Machine, State
from app.core.logging_config import get_logger
from app.schemas.pipeline import PipelinePhase, PipelineStatus, PipelineProgress, PhaseResult

logger = get_logger(__name__)


class PipelineStateMachine:
    """
    State machine for the 9-phase story generation pipeline.
    
    Phases:
    1. CONCEPT - Concept development
    2. OUTLINE - Outline generation
    3. BEAT_SHEET - Beat sheet creation
    4. DRAFTING - Draft writing
    5. CRITIQUE - Critique and analysis
    6. REWRITE - Rewriting based on critique
    7. POLISH - Polishing and refinement
    8. CONSISTENCY - Consistency checking
    9. EXPORT - Export and finalization
    """
    
    # Define the 9 phases in order
    PHASES = [
        PipelinePhase.CONCEPT,
        PipelinePhase.OUTLINE,
        PipelinePhase.BEAT_SHEET,
        PipelinePhase.DRAFTING,
        PipelinePhase.CRITIQUE,
        PipelinePhase.REWRITE,
        PipelinePhase.POLISH,
        PipelinePhase.CONSISTENCY,
        PipelinePhase.EXPORT,
    ]
    
    def __init__(self, story_id: str, pipeline_id: Optional[str] = None):
        self.story_id = story_id
        self.pipeline_id = pipeline_id or str(uuid.uuid4())
        self.status = PipelineStatus.PENDING
        self.current_phase: Optional[PipelinePhase] = None
        self.progress = PipelineProgress(
            current_phase=PipelinePhase.CONCEPT,
            overall_status=self.status,
        )
        self.phase_results: Dict[PipelinePhase, PhaseResult] = {}
        self.metadata: Dict[str, Any] = {}
        self.checkpoint_data: Optional[Dict[str, Any]] = None
        
        self.started_at: Optional[datetime] = None
        self.completed_at: Optional[datetime] = None
        
        # Initialize state machine
        self._init_state_machine()
        
        logger.info("Pipeline state machine created", pipeline_id=self.pipeline_id)
    
    def _init_state_machine(self) -> None:
        """Initialize the state machine with states and transitions."""
        
        # Define states
        states = [
            State(name='idle', on_enter=self._on_idle),
            State(name='concept', on_enter=self._on_concept),
            State(name='outline', on_enter=self._on_outline),
            State(name='beat_sheet', on_enter=self._on_beat_sheet),
            State(name='drafting', on_enter=self._on_drafting),
            State(name='critique', on_enter=self._on_critique),
            State(name='rewrite', on_enter=self._on_rewrite),
            State(name='polish', on_enter=self._on_polish),
            State(name='consistency', on_enter=self._on_consistency),
            State(name='export', on_enter=self._on_export),
            State(name='completed', on_enter=self._on_completed),
            State(name='failed', on_enter=self._on_failed),
            State(name='waiting_approval', on_enter=self._on_waiting_approval),
            State(name='paused', on_enter=self._on_paused),
        ]
        
        # Define transitions
        transitions = [
            # Start pipeline
            {'trigger': 'start', 'source': 'idle', 'dest': 'concept'},
            
            # Phase transitions (forward)
            {'trigger': 'next_phase', 'source': 'concept', 'dest': 'outline'},
            {'trigger': 'next_phase', 'source': 'outline', 'dest': 'beat_sheet'},
            {'trigger': 'next_phase', 'source': 'beat_sheet', 'dest': 'drafting'},
            {'trigger': 'next_phase', 'source': 'drafting', 'dest': 'critique'},
            {'trigger': 'next_phase', 'source': 'critique', 'dest': 'rewrite'},
            {'trigger': 'next_phase', 'source': 'rewrite', 'dest': 'polish'},
            {'trigger': 'next_phase', 'source': 'polish', 'dest': 'consistency'},
            {'trigger': 'next_phase', 'source': 'consistency', 'dest': 'export'},
            {'trigger': 'next_phase', 'source': 'export', 'dest': 'completed'},
            
            # Phase transitions (backward for revisions)
            {'trigger': 'previous_phase', 'source': '*', 'dest': '='},  # Custom handler
            
            # Approval gating
            {'trigger': 'require_approval', 'source': '*', 'dest': 'waiting_approval'},
            {'trigger': 'approve', 'source': 'waiting_approval', 'dest': '='},  # Custom handler
            {'trigger': 'reject', 'source': 'waiting_approval', 'dest': '='},  # Custom handler
            
            # Control flows
            {'trigger': 'pause', 'source': '*', 'dest': 'paused'},
            {'trigger': 'resume', 'source': 'paused', 'dest': '='},  # Custom handler
            {'trigger': 'fail', 'source': '*', 'dest': 'failed'},
            {'trigger': 'retry', 'source': 'failed', 'dest': '='},  # Custom handler
            {'trigger': 'complete', 'source': 'export', 'dest': 'completed'},
        ]
        
        # Create the machine
        self.machine = Machine(
            model=self,
            states=states,
            transitions=transitions,
            initial='idle',
            send_event=True,
        )
    
    # State entry handlers
    
    def _on_idle(self, event) -> None:
        logger.debug("Pipeline entered idle state", pipeline_id=self.pipeline_id)
        self.status = PipelineStatus.PENDING
        self.current_phase = None
    
    def _on_concept(self, event) -> None:
        logger.info("Pipeline entered CONCEPT phase", pipeline_id=self.pipeline_id)
        self.current_phase = PipelinePhase.CONCEPT
        self.status = PipelineStatus.RUNNING
        self._update_progress()
    
    def _on_outline(self, event) -> None:
        logger.info("Pipeline entered OUTLINE phase", pipeline_id=self.pipeline_id)
        self.current_phase = PipelinePhase.OUTLINE
        self.status = PipelineStatus.RUNNING
        self._update_progress()
    
    def _on_beat_sheet(self, event) -> None:
        logger.info("Pipeline entered BEAT_SHEET phase", pipeline_id=self.pipeline_id)
        self.current_phase = PipelinePhase.BEAT_SHEET
        self.status = PipelineStatus.RUNNING
        self._update_progress()
    
    def _on_drafting(self, event) -> None:
        logger.info("Pipeline entered DRAFTING phase", pipeline_id=self.pipeline_id)
        self.current_phase = PipelinePhase.DRAFTING
        self.status = PipelineStatus.RUNNING
        self._update_progress()
    
    def _on_critique(self, event) -> None:
        logger.info("Pipeline entered CRITIQUE phase", pipeline_id=self.pipeline_id)
        self.current_phase = PipelinePhase.CRITIQUE
        self.status = PipelineStatus.RUNNING
        self._update_progress()
    
    def _on_rewrite(self, event) -> None:
        logger.info("Pipeline entered REWRITE phase", pipeline_id=self.pipeline_id)
        self.current_phase = PipelinePhase.REWRITE
        self.status = PipelineStatus.RUNNING
        self._update_progress()
    
    def _on_polish(self, event) -> None:
        logger.info("Pipeline entered POLISH phase", pipeline_id=self.pipeline_id)
        self.current_phase = PipelinePhase.POLISH
        self.status = PipelineStatus.RUNNING
        self._update_progress()
    
    def _on_consistency(self, event) -> None:
        logger.info("Pipeline entered CONSISTENCY phase", pipeline_id=self.pipeline_id)
        self.current_phase = PipelinePhase.CONSISTENCY
        self.status = PipelineStatus.RUNNING
        self._update_progress()
    
    def _on_export(self, event) -> None:
        logger.info("Pipeline entered EXPORT phase", pipeline_id=self.pipeline_id)
        self.current_phase = PipelinePhase.EXPORT
        self.status = PipelineStatus.RUNNING
        self._update_progress()
    
    def _on_completed(self, event) -> None:
        logger.info("Pipeline completed successfully", pipeline_id=self.pipeline_id)
        self.status = PipelineStatus.COMPLETED
        self.completed_at = datetime.utcnow()
        self.progress.overall_status = PipelineStatus.COMPLETED
        self.progress.progress_percentage = 100.0
    
    def _on_failed(self, event) -> None:
        logger.error("Pipeline failed", pipeline_id=self.pipeline_id, error=event.kwargs.get('error'))
        self.status = PipelineStatus.FAILED
        self.progress.overall_status = PipelineStatus.FAILED
    
    def _on_waiting_approval(self, event) -> None:
        logger.info("Pipeline waiting for approval", pipeline_id=self.pipeline_id)
        self.status = PipelineStatus.WAITING_APPROVAL
    
    def _on_paused(self, event) -> None:
        logger.info("Pipeline paused", pipeline_id=self.pipeline_id)
        self.status = PipelineStatus.PAUSED
    
    # Helper methods
    
    def _update_progress(self) -> None:
        """Update progress percentage based on current phase."""
        if self.current_phase:
            phase_index = self.PHASES.index(self.current_phase)
            self.progress.progress_percentage = ((phase_index + 1) / len(self.PHASES)) * 100
        self.progress.overall_status = self.status
        self.progress.current_phase = self.current_phase
    
    def _get_previous_phase(self) -> Optional[PipelinePhase]:
        """Get the previous phase in the pipeline."""
        if not self.current_phase:
            return None
        current_index = self.PHASES.index(self.current_phase)
        if current_index > 0:
            return self.PHASES[current_index - 1]
        return None
    
    # Custom transition handlers
    
    def go_to_previous_phase(self) -> bool:
        """Transition to the previous phase."""
        previous = self._get_previous_phase()
        if previous:
            self.current_phase = previous
            self.status = PipelineStatus.RUNNING
            self._update_progress()
            logger.info("Moved to previous phase", phase=previous.value)
            return True
        return False
    
    def approve_and_continue(self) -> bool:
        """Approve and continue to next phase."""
        if self.status == PipelineStatus.WAITING_APPROVAL:
            # Determine next phase based on current context
            self.status = PipelineStatus.RUNNING
            self._update_progress()
            logger.info("Approval granted, continuing pipeline")
            return True
        return False
    
    def reject_and_revision(self, target_phase: Optional[PipelinePhase] = None) -> bool:
        """Reject and go back for revision."""
        if self.status == PipelineStatus.WAITING_APPROVAL:
            if target_phase:
                self.current_phase = target_phase
            else:
                self.go_to_previous_phase()
            self.status = PipelineStatus.RUNNING
            self._update_progress()
            logger.info("Rejection - sent for revision", phase=self.current_phase)
            return True
        return False
    
    def resume_from_pause(self) -> bool:
        """Resume from paused state."""
        if self.status == PipelineStatus.PAUSED:
            self.status = PipelineStatus.RUNNING
            self._update_progress()
            logger.info("Pipeline resumed")
            return True
        return False
    
    def retry_from_failure(self) -> bool:
        """Retry from failed state."""
        if self.status == PipelineStatus.FAILED:
            self.status = PipelineStatus.RUNNING
            self._update_progress()
            logger.info("Pipeline retry initiated")
            return True
        return False
    
    # Phase result tracking
    
    def record_phase_result(
        self,
        phase: PipelinePhase,
        status: str,
        output: Dict[str, Any],
        errors: Optional[List[str]] = None,
        requires_approval: bool = False,
    ) -> None:
        """Record the result of a phase execution."""
        result = PhaseResult(
            phase=phase,
            status=status,
            output=output,
            errors=errors or [],
            requires_approval=requires_approval,
            approval_status="pending" if requires_approval else None,
            completed_at=datetime.utcnow() if status != "running" else None,
        )
        
        self.phase_results[phase] = result
        self.metadata[f"{phase.value}_completed_at"] = datetime.utcnow().isoformat()
        
        logger.info(
            "Phase result recorded",
            phase=phase.value,
            status=status,
            requires_approval=requires_approval,
        )
    
    def get_phase_result(self, phase: PipelinePhase) -> Optional[PhaseResult]:
        """Get the result of a specific phase."""
        return self.phase_results.get(phase)
    
    def get_all_phase_results(self) -> Dict[PipelinePhase, PhaseResult]:
        """Get all phase results."""
        return self.phase_results
    
    # Checkpointing
    
    def save_checkpoint(self, data: Dict[str, Any]) -> None:
        """Save checkpoint data for recovery."""
        self.checkpoint_data = {
            "timestamp": datetime.utcnow().isoformat(),
            "state": self.state,
            "status": self.status.value,
            "current_phase": self.current_phase.value if self.current_phase else None,
            "data": data,
        }
        logger.debug("Checkpoint saved", pipeline_id=self.pipeline_id)
    
    def load_checkpoint(self, checkpoint_data: Dict[str, Any]) -> bool:
        """Load checkpoint data for recovery."""
        try:
            self.checkpoint_data = checkpoint_data
            self.state = checkpoint_data.get("state", "idle")
            self.status = PipelineStatus(checkpoint_data.get("status", "pending"))
            
            phase_value = checkpoint_data.get("current_phase")
            if phase_value:
                self.current_phase = PipelinePhase(phase_value)
            
            self._update_progress()
            logger.info("Checkpoint loaded", pipeline_id=self.pipeline_id)
            return True
        except Exception as e:
            logger.error("Failed to load checkpoint", error=str(e))
            return False
    
    # Status and info
    
    def get_status(self) -> Dict[str, Any]:
        """Get current pipeline status."""
        return {
            "pipeline_id": self.pipeline_id,
            "story_id": self.story_id,
            "state": self.state,
            "status": self.status.value,
            "current_phase": self.current_phase.value if self.current_phase else None,
            "progress_percentage": self.progress.progress_percentage,
            "started_at": self.started_at.isoformat() if self.started_at else None,
            "completed_at": self.completed_at.isoformat() if self.completed_at else None,
            "phase_results": {
                phase.value: result.model_dump()
                for phase, result in self.phase_results.items()
            },
        }
    
    def start(self) -> bool:
        """Start the pipeline."""
        if self.state == 'idle':
            self.started_at = datetime.utcnow()
            self.trigger('start')
            logger.info("Pipeline started", pipeline_id=self.pipeline_id)
            return True
        return False
