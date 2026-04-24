"""
Base Agent class for all Narrative Nexus agents.
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, List
from datetime import datetime
from pydantic import BaseModel, Field

from app.core.logging_config import get_logger

logger = get_logger(__name__)


class AgentResponse(BaseModel):
    """Standard response from an agent."""
    success: bool
    data: Dict[str, Any] = Field(default_factory=dict)
    errors: List[str] = Field(default_factory=list)
    warnings: List[str] = Field(default_factory=list)
    requires_approval: bool = False
    metadata: Dict[str, Any] = Field(default_factory=dict)


class BaseAgent(ABC):
    """
    Abstract base class for all pipeline agents.
    Each agent handles a specific phase of the story generation pipeline.
    """
    
    def __init__(self, name: str):
        self.name = name
        self.created_at = datetime.utcnow()
    
    @abstractmethod
    async def execute(
        self,
        story_id: str,
        context: Dict[str, Any],
    ) -> AgentResponse:
        """
        Execute the agent's task.
        
        Args:
            story_id: The ID of the story being processed
            context: Current context including previous phase outputs
            
        Returns:
            AgentResponse with results
        """
        pass
    
    async def _get_llm_response(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        **kwargs,
    ) -> str:
        """
        Get a response from the LLM.
        
        This is a placeholder that will be implemented with actual LLM integration.
        """
        # TODO: Implement LiteLLM/Ollama integration
        logger.info("LLM request", agent=self.name, prompt_length=len(prompt))
        return "LLM response placeholder"
    
    async def _validate_output(
        self,
        output: Dict[str, Any],
        required_fields: List[str],
    ) -> List[str]:
        """Validate that output contains required fields."""
        errors = []
        for field in required_fields:
            if field not in output:
                errors.append(f"Missing required field: {field}")
        return errors
    
    def _create_response(
        self,
        success: bool,
        data: Optional[Dict[str, Any]] = None,
        errors: Optional[List[str]] = None,
        warnings: Optional[List[str]] = None,
        requires_approval: bool = False,
    ) -> AgentResponse:
        """Create a standard agent response."""
        return AgentResponse(
            success=success,
            data=data or {},
            errors=errors or [],
            warnings=warnings or [],
            requires_approval=requires_approval,
            metadata={
                "agent": self.name,
                "timestamp": datetime.utcnow().isoformat(),
            },
        )
    
    async def preprocess_context(
        self,
        context: Dict[str, Any],
    ) -> Dict[str, Any]:
        """Preprocess context before execution."""
        return context
    
    async def postprocess_result(
        self,
        result: AgentResponse,
    ) -> AgentResponse:
        """Postprocess result after execution."""
        return result
    
    async def run(
        self,
        story_id: str,
        context: Dict[str, Any],
    ) -> AgentResponse:
        """
        Run the agent with preprocessing and postprocessing.
        """
        try:
            logger.info("Agent starting", agent=self.name, story_id=story_id)
            
            # Preprocess
            processed_context = await self.preprocess_context(context)
            
            # Execute
            result = await self.execute(story_id, processed_context)
            
            # Postprocess
            final_result = await self.postprocess_result(result)
            
            logger.info("Agent completed", agent=self.name, success=final_result.success)
            return final_result
            
        except Exception as e:
            logger.error("Agent failed", agent=self.name, error=str(e))
            return self._create_response(
                success=False,
                errors=[str(e)],
            )
