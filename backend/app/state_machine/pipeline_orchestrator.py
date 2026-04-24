"""
Pipeline Orchestrator - Coordinates the 9-phase story generation pipeline.
"""

from typing import Dict, Any, Optional, Callable, Awaitable
from datetime import datetime
import uuid

from app.core.logging_config import get_logger
from app.schemas.pipeline import PipelinePhase, PipelineStatus
from app.state_machine.pipeline_state_machine import PipelineStateMachine
from app.memory import MemoryManager

logger = get_logger(__name__)


# Type alias for phase handlers
PhaseHandler = Callable[[str, Dict[str, Any]], Awaitable[Dict[str, Any]]]


class PipelineOrchestrator:
    """
    Orchestrates the execution of the 9-phase story generation pipeline.
    Manages phase handlers, human-in-the-loop gating, and progress tracking.
    """
    
    def __init__(self, memory_manager: MemoryManager):
        self.memory_manager = memory_manager
        self.pipelines: Dict[str, PipelineStateMachine] = {}
        self.phase_handlers: Dict[PipelinePhase, PhaseHandler] = {}
        self.approval_callbacks: Dict[str, Callable] = {}
        
        self._register_default_handlers()
    
    def _register_default_handlers(self) -> None:
        """Register default phase handlers (to be implemented in agents module)."""
        # These will be replaced with actual agent implementations in Phase D
        self.phase_handlers = {
            PipelinePhase.CONCEPT: self._default_handler,
            PipelinePhase.OUTLINE: self._default_handler,
            PipelinePhase.BEAT_SHEET: self._default_handler,
            PipelinePhase.DRAFTING: self._default_handler,
            PipelinePhase.CRITIQUE: self._default_handler,
            PipelinePhase.REWRITE: self._default_handler,
            PipelinePhase.POLISH: self._default_handler,
            PipelinePhase.CONSISTENCY: self._default_handler,
            PipelinePhase.EXPORT: self._default_handler,
        }
    
    async def _default_handler(
        self,
        story_id: str,
        context: Dict[str, Any],
    ) -> Dict[str, Any]:
        """Default placeholder handler."""
        return {"status": "placeholder", "message": "Handler not yet implemented"}
    
    def register_phase_handler(
        self,
        phase: PipelinePhase,
        handler: PhaseHandler,
    ) -> None:
        """Register a handler for a specific phase."""
        self.phase_handlers[phase] = handler
        logger.info("Phase handler registered", phase=phase.value)
    
    def register_approval_callback(
        self,
        pipeline_id: str,
        callback: Callable,
    ) -> None:
        """Register a callback for approval notifications."""
        self.approval_callbacks[pipeline_id] = callback
    
    async def create_pipeline(self, story_id: str) -> str:
        """Create a new pipeline for a story."""
        pipeline = PipelineStateMachine(story_id=story_id)
        self.pipelines[pipeline.pipeline_id] = pipeline
        
        logger.info("Pipeline created", pipeline_id=pipeline.pipeline_id, story_id=story_id)
        return pipeline.pipeline_id
    
    def get_pipeline(self, pipeline_id: str) -> Optional[PipelineStateMachine]:
        """Get a pipeline by ID."""
        return self.pipelines.get(pipeline_id)
    
    async def execute_phase(
        self,
        pipeline_id: str,
        phase: PipelinePhase,
        context: Dict[str, Any],
    ) -> Dict[str, Any]:
        """Execute a specific phase of the pipeline."""
        pipeline = self.get_pipeline(pipeline_id)
        if not pipeline:
            raise ValueError(f"Pipeline {pipeline_id} not found")
        
        handler = self.phase_handlers.get(phase)
        if not handler:
            raise ValueError(f"No handler registered for phase {phase.value}")
        
        try:
            logger.info("Executing phase", pipeline_id=pipeline_id, phase=phase.value)
            
            # Execute the phase handler
            result = await handler(pipeline.story_id, context)
            
            # Record the result
            pipeline.record_phase_result(
                phase=phase,
                status="completed",
                output=result,
                requires_approval=result.get("requires_approval", False),
            )
            
            # Check if approval is required
            if result.get("requires_approval"):
                pipeline.require_approval()
                
                # Notify via callback
                callback = self.approval_callbacks.get(pipeline_id)
                if callback:
                    await callback(pipeline_id, phase, result)
            
            return result
            
        except Exception as e:
            logger.error("Phase execution failed", pipeline_id=pipeline_id, phase=phase.value, error=str(e))
            pipeline.record_phase_result(
                phase=phase,
                status="failed",
                output={},
                errors=[str(e)],
            )
            pipeline.fail(error=str(e))
            raise
    
    async def run_pipeline(
        self,
        pipeline_id: str,
        initial_context: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """Run the complete pipeline from start to finish."""
        pipeline = self.get_pipeline(pipeline_id)
        if not pipeline:
            raise ValueError(f"Pipeline {pipeline_id} not found")
        
        # Start the pipeline
        pipeline.start()
        
        context = initial_context or {}
        results = {}
        
        try:
            for phase in PipelineStateMachine.PHASES:
                # Check if pipeline should continue
                if pipeline.status == PipelineStatus.PAUSED:
                    logger.info("Pipeline paused, waiting for resume")
                    break
                
                if pipeline.status == PipelineStatus.WAITING_APPROVAL:
                    logger.info("Pipeline waiting for approval")
                    break
                
                # Execute the phase
                phase_result = await self.execute_phase(pipeline_id, phase, context)
                results[phase.value] = phase_result
                
                # Update context with phase output
                context.update(phase_result)
                
                # Move to next phase if no approval required
                if not phase_result.get("requires_approval"):
                    if phase != PipelineStateMachine.PHASES[-1]:
                        pipeline.next_phase()
                
            return {
                "pipeline_id": pipeline_id,
                "status": pipeline.status.value,
                "results": results,
                "context": context,
            }
            
        except Exception as e:
            logger.error("Pipeline execution failed", pipeline_id=pipeline_id, error=str(e))
            raise
    
    async def approve_phase(self, pipeline_id: str) -> bool:
        """Approve the current phase and continue."""
        pipeline = self.get_pipeline(pipeline_id)
        if not pipeline:
            return False
        
        if pipeline.approve_and_continue():
            # Move to next phase
            if pipeline.current_phase and pipeline.current_phase != PipelineStateMachine.PHASES[-1]:
                pipeline.next_phase()
            return True
        
        return False
    
    async def reject_phase(
        self,
        pipeline_id: str,
        target_phase: Optional[PipelinePhase] = None,
    ) -> bool:
        """Reject the current phase and send for revision."""
        pipeline = self.get_pipeline(pipeline_id)
        if not pipeline:
            return False
        
        return pipeline.reject_and_revision(target_phase)
    
    async def pause_pipeline(self, pipeline_id: str) -> bool:
        """Pause a running pipeline."""
        pipeline = self.get_pipeline(pipeline_id)
        if not pipeline:
            return False
        
        pipeline.pause()
        return True
    
    async def resume_pipeline(self, pipeline_id: str) -> bool:
        """Resume a paused pipeline."""
        pipeline = self.get_pipeline(pipeline_id)
        if not pipeline:
            return False
        
        return pipeline.resume_from_pause()
    
    def get_pipeline_status(self, pipeline_id: str) -> Optional[Dict[str, Any]]:
        """Get the current status of a pipeline."""
        pipeline = self.get_pipeline(pipeline_id)
        if not pipeline:
            return None
        
        return pipeline.get_status()
    
    def list_pipelines(self, story_id: Optional[str] = None) -> list:
        """List all pipelines, optionally filtered by story_id."""
        pipelines = []
        for pipeline in self.pipelines.values():
            if story_id is None or pipeline.story_id == story_id:
                pipelines.append(pipeline.get_status())
        return pipelines
    
    async def save_checkpoint(self, pipeline_id: str) -> bool:
        """Save a checkpoint for a pipeline."""
        pipeline = self.get_pipeline(pipeline_id)
        if not pipeline:
            return False
        
        checkpoint_data = {
            "context": {},  # Would include current context
            "phase_results": pipeline.get_all_phase_results(),
        }
        
        pipeline.save_checkpoint(checkpoint_data)
        return True
    
    async def load_checkpoint(
        self,
        pipeline_id: str,
        checkpoint_data: Dict[str, Any],
    ) -> bool:
        """Load a checkpoint for a pipeline."""
        pipeline = self.get_pipeline(pipeline_id)
        if not pipeline:
            return False
        
        return pipeline.load_checkpoint(checkpoint_data)
