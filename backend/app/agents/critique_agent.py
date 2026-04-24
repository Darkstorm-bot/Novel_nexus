"""
Critique Agent - Phase 5 of the pipeline.
Analyzes draft and provides critical feedback.
"""

from typing import Dict, Any, List
import json

from app.agents.base_agent import BaseAgent, AgentResponse
from app.core.logging_config import get_logger

logger = get_logger(__name__)


class CritiqueAgent(BaseAgent):
    """
    Agent responsible for critiquing drafts.
    
    Tasks:
    - Analyze plot structure
    - Evaluate character development
    - Assess pacing
    - Identify inconsistencies
    - Provide improvement suggestions
    """
    
    def __init__(self):
        super().__init__("CritiqueAgent")
    
    async def execute(
        self,
        story_id: str,
        context: Dict[str, Any],
    ) -> AgentResponse:
        try:
            logger.info("Starting critique analysis", story_id=story_id)
            
            draft_data = context.get("draft_data", {})
            if not draft_data:
                return self._create_response(
                    success=False,
                    errors=["No draft data provided."],
                )
            
            system_prompt = self._build_system_prompt()
            prompt = self._build_critique_prompt(draft_data, context)
            
            llm_response = await self._get_llm_response(prompt, system_prompt)
            critique_data = self._parse_critique_response(llm_response)
            
            required_fields = ["analysis", "issues", "suggestions"]
            errors = await self._validate_output(critique_data, required_fields)
            
            if errors:
                return self._create_response(success=False, errors=errors)
            
            return self._create_response(
                success=True,
                data=critique_data,
                requires_approval=True,
                metadata={"phase": "critique", "critique_complete": True}
            )
            
        except Exception as e:
            logger.error("Critique failed", story_id=story_id, error=str(e))
            return self._create_response(success=False, errors=[str(e)])
    
    def _build_system_prompt(self) -> str:
        return """You are an expert literary critic and editor.
Provide comprehensive critique including:
- Plot analysis
- Character development assessment
- Pacing evaluation
- Consistency check
- Specific improvement suggestions

Format as JSON:
{
    "analysis": {
        "plot": "string",
        "characters": "string",
        "pacing": "string",
        "voice": "string"
    },
    "issues": [
        {
            "type": "plot|character|pacing|consistency",
            "severity": "low|medium|high",
            "description": "string",
            "location": "chapter X"
        }
    ],
    "suggestions": [
        {
            "issue_ref": 0,
            "suggestion": "string"
        }
    ],
    "strengths": ["list"],
    "overall_score": 1-10
}"""
    
    def _build_critique_prompt(
        self,
        draft_data: Dict[str, Any],
        context: Dict[str, Any],
    ) -> str:
        chapters = draft_data.get("chapters", [])
        word_count = draft_data.get("total_word_count", 0)
        return f"Critique this {word_count}-word draft with {len(chapters)} chapters. Be thorough and constructive."
    
    def _parse_critique_response(self, response: str) -> Dict[str, Any]:
        try:
            start_idx = response.find("{")
            end_idx = response.rfind("}") + 1
            if start_idx >= 0 and end_idx > start_idx:
                return json.loads(response[start_idx:end_idx])
        except json.JSONDecodeError:
            pass
        return {"analysis": {}, "issues": [], "suggestions": [], "strengths": []}
    
    async def postprocess_result(self, result: AgentResponse) -> AgentResponse:
        if result.success and result.data:
            issue_count = len(result.data.get("issues", []))
            result.data["summary"] = f"Critique complete: {issue_count} issues identified"
        return result
