"""
Polish Agent - Phase 7 of the pipeline.
Polishes and refines the rewritten draft.
"""

from typing import Dict, Any, List
import json

from app.agents.base_agent import BaseAgent, AgentResponse
from app.core.logging_config import get_logger

logger = get_logger(__name__)


class PolishAgent(BaseAgent):
    """
    Agent responsible for polishing prose.
    
    Tasks:
    - Improve sentence flow
    - Enhance word choice
    - Fix grammar and style
    - Refine dialogue
    - Smooth transitions
    """
    
    def __init__(self):
        super().__init__("PolishAgent")
    
    async def execute(
        self,
        story_id: str,
        context: Dict[str, Any],
    ) -> AgentResponse:
        try:
            logger.info("Starting polish", story_id=story_id)
            
            rewrite_data = context.get("rewrite_data", {})
            if not rewrite_data:
                return self._create_response(
                    success=False,
                    errors=["No rewrite data provided."],
                )
            
            system_prompt = self._build_system_prompt()
            prompt = self._build_polish_prompt(rewrite_data, context)
            
            llm_response = await self._get_llm_response(prompt, system_prompt)
            polish_data = self._parse_polish_response(llm_response)
            
            required_fields = ["chapters", "polishing_notes"]
            errors = await self._validate_output(polish_data, required_fields)
            
            if errors:
                return self._create_response(success=False, errors=errors)
            
            return self._create_response(
                success=True,
                data=polish_data,
                requires_approval=True,
                metadata={"phase": "polish", "polish_complete": True}
            )
            
        except Exception as e:
            logger.error("Polish failed", story_id=story_id, error=str(e))
            return self._create_response(success=False, errors=[str(e)])
    
    def _build_system_prompt(self) -> str:
        return """You are an expert line editor and prose stylist.
Polish the text for:
- Sentence rhythm and flow
- Word choice and variety
- Grammar and punctuation
- Dialogue naturalness
- Smooth transitions

Format as JSON:
{
    "chapters": [
        {
            "chapter_number": 1,
            "title": "string",
            "content": "polished chapter text",
            "word_count": 0,
            "improvements": ["list of specific improvements"]
        }
    ],
    "polishing_notes": "string",
    "style_improvements": ["list"],
    "total_word_count": 0
}"""
    
    def _build_polish_prompt(
        self,
        rewrite_data: Dict[str, Any],
        context: Dict[str, Any],
    ) -> str:
        chapters = rewrite_data.get("chapters", [])
        word_count = rewrite_data.get("total_word_count", 0)
        return f"Polish this {word_count}-word draft ({len(chapters)} chapters). Focus on prose quality, flow, and readability."
    
    def _parse_polish_response(self, response: str) -> Dict[str, Any]:
        try:
            start_idx = response.find("{")
            end_idx = response.rfind("}") + 1
            if start_idx >= 0 and end_idx > start_idx:
                return json.loads(response[start_idx:end_idx])
        except json.JSONDecodeError:
            pass
        return {"chapters": [], "polishing_notes": "", "style_improvements": []}
    
    async def postprocess_result(self, result: AgentResponse) -> AgentResponse:
        if result.success and result.data:
            improvements = len(result.data.get("style_improvements", []))
            result.data["summary"] = f"Polish complete: {improvements} style improvements"
        return result
