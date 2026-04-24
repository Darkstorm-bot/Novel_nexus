"""
Rewrite Agent - Phase 6 of the pipeline.
Rewrites draft based on critique feedback.
"""

from typing import Dict, Any, List
import json

from app.agents.base_agent import BaseAgent, AgentResponse
from app.core.logging_config import get_logger

logger = get_logger(__name__)


class RewriteAgent(BaseAgent):
    """
    Agent responsible for rewriting drafts based on critique.
    
    Tasks:
    - Address identified issues
    - Improve weak areas
    - Enhance strengths
    - Maintain consistency
    """
    
    def __init__(self):
        super().__init__("RewriteAgent")
    
    async def execute(
        self,
        story_id: str,
        context: Dict[str, Any],
    ) -> AgentResponse:
        try:
            logger.info("Starting rewrite", story_id=story_id)
            
            draft_data = context.get("draft_data", {})
            critique_data = context.get("critique_data", {})
            
            if not draft_data:
                return self._create_response(
                    success=False,
                    errors=["No draft data provided."],
                )
            
            system_prompt = self._build_system_prompt()
            prompt = self._build_rewrite_prompt(draft_data, critique_data, context)
            
            llm_response = await self._get_llm_response(prompt, system_prompt)
            rewrite_data = self._parse_rewrite_response(llm_response)
            
            required_fields = ["chapters", "changes_made"]
            errors = await self._validate_output(rewrite_data, required_fields)
            
            if errors:
                return self._create_response(success=False, errors=errors)
            
            await self._store_rewrite_memory(story_id, rewrite_data, context)
            
            return self._create_response(
                success=True,
                data=rewrite_data,
                requires_approval=True,
                metadata={"phase": "rewrite", "rewrite_complete": True}
            )
            
        except Exception as e:
            logger.error("Rewrite failed", story_id=story_id, error=str(e))
            return self._create_response(success=False, errors=[str(e)])
    
    def _build_system_prompt(self) -> str:
        return """You are an expert fiction editor and writer.
Rewrite the draft addressing all critique issues while maintaining voice and style.

Format as JSON:
{
    "chapters": [
        {
            "chapter_number": 1,
            "title": "string",
            "content": "revised chapter text",
            "word_count": 0,
            "changes_summary": "what was changed"
        }
    ],
    "changes_made": [
        {
            "issue_addressed": "string",
            "change_type": "addition|deletion|revision",
            "location": "chapter X",
            "description": "string"
        }
    ],
    "total_word_count": 0,
    "revision_notes": "string"
}"""
    
    def _build_rewrite_prompt(
        self,
        draft_data: Dict[str, Any],
        critique_data: Dict[str, Any],
        context: Dict[str, Any],
    ) -> str:
        issues = critique_data.get("issues", [])
        suggestions = critique_data.get("suggestions", [])
        
        return f"""Rewrite the draft addressing these {len(issues)} issues:
{json.dumps(issues[:5], indent=2)}...

Implement these suggestions where appropriate:
{json.dumps(suggestions[:5], indent=2)}...

Maintain the original voice while improving weak areas."""
    
    def _parse_rewrite_response(self, response: str) -> Dict[str, Any]:
        try:
            start_idx = response.find("{")
            end_idx = response.rfind("}") + 1
            if start_idx >= 0 and end_idx > start_idx:
                return json.loads(response[start_idx:end_idx])
        except json.JSONDecodeError:
            pass
        return {"chapters": [], "changes_made": [], "total_word_count": 0}
    
    async def _store_rewrite_memory(
        self,
        story_id: str,
        rewrite_data: Dict[str, Any],
        context: Dict[str, Any],
    ) -> None:
        memory_manager = context.get("memory_manager")
        if not memory_manager:
            return
        
        from app.schemas.memory import MemoryType
        
        for change in rewrite_data.get("changes_made", []):
            await memory_manager.store_episodic_memory(
                content=change.get("description", ""),
                story_id=story_id,
                event_type="revision",
                metadata={"change_type": change.get("change_type")},
                importance=0.5,
            )
    
    async def postprocess_result(self, result: AgentResponse) -> AgentResponse:
        if result.success and result.data:
            changes = len(result.data.get("changes_made", []))
            result.data["summary"] = f"Rewrite complete: {changes} changes made"
        return result
