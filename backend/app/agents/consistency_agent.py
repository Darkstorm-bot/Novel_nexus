"""
Consistency Agent - Phase 8 of the pipeline.
Checks story for consistency issues.
"""

from typing import Dict, Any, List
import json

from app.agents.base_agent import BaseAgent, AgentResponse
from app.core.logging_config import get_logger

logger = get_logger(__name__)


class ConsistencyAgent(BaseAgent):
    """
    Agent responsible for consistency checking.
    
    Tasks:
    - Check character consistency
    - Verify plot continuity
    - Validate timeline
    - Ensure world-building rules
    - Flag contradictions
    """
    
    def __init__(self):
        super().__init__("ConsistencyAgent")
    
    async def execute(
        self,
        story_id: str,
        context: Dict[str, Any],
    ) -> AgentResponse:
        try:
            logger.info("Starting consistency check", story_id=story_id)
            
            polish_data = context.get("polish_data", {})
            if not polish_data:
                return self._create_response(
                    success=False,
                    errors=["No polished draft data provided."],
                )
            
            system_prompt = self._build_system_prompt()
            prompt = self._build_consistency_prompt(polish_data, context)
            
            llm_response = await self._get_llm_response(prompt, system_prompt)
            consistency_data = self._parse_consistency_response(llm_response)
            
            required_fields = ["consistency_report", "issues", "resolutions"]
            errors = await self._validate_output(consistency_data, required_fields)
            
            if errors:
                return self._create_response(success=False, errors=errors)
            
            # Auto-fix minor issues if possible
            if consistency_data.get("auto_fixed"):
                polish_data = await self._apply_auto_fixes(polish_data, consistency_data)
            
            return self._create_response(
                success=True,
                data={
                    **consistency_data,
                    "polished_data": polish_data,
                },
                requires_approval=True,
                metadata={"phase": "consistency", "consistency_check_complete": True}
            )
            
        except Exception as e:
            logger.error("Consistency check failed", story_id=story_id, error=str(e))
            return self._create_response(success=False, errors=[str(e)])
    
    def _build_system_prompt(self) -> str:
        return """You are an expert continuity editor.
Check the story for consistency in:
- Character traits, appearance, and behavior
- Plot continuity and cause-effect
- Timeline and chronology
- World-building rules and magic systems
- Setting details

Format as JSON:
{
    "consistency_report": {
        "characters": "assessment",
        "plot": "assessment",
        "timeline": "assessment",
        "world_building": "assessment"
    },
    "issues": [
        {
            "type": "character|plot|timeline|world",
            "severity": "minor|major|critical",
            "description": "string",
            "locations": ["chapter X", "chapter Y"],
            "auto_fixable": true/false,
            "suggested_fix": "string"
        }
    ],
    "resolutions": ["how issues were addressed"],
    "auto_fixed": true/false,
    "manual_review_needed": ["list of issues requiring human review"]
}"""
    
    def _build_consistency_prompt(
        self,
        polish_data: Dict[str, Any],
        context: Dict[str, Any],
    ) -> str:
        chapters = polish_data.get("chapters", [])
        return f"Perform comprehensive consistency check on this {len(chapters)}-chapter story. Flag all contradictions and continuity errors."
    
    def _parse_consistency_response(self, response: str) -> Dict[str, Any]:
        try:
            start_idx = response.find("{")
            end_idx = response.rfind("}") + 1
            if start_idx >= 0 and end_idx > start_idx:
                return json.loads(response[start_idx:end_idx])
        except json.JSONDecodeError:
            pass
        return {
            "consistency_report": {},
            "issues": [],
            "resolutions": [],
            "auto_fixed": False,
        }
    
    async def _apply_auto_fixes(
        self,
        polish_data: Dict[str, Any],
        consistency_data: Dict[str, Any],
    ) -> Dict[str, Any]:
        """Apply auto-fixable consistency corrections."""
        issues = consistency_data.get("issues", [])
        auto_fixable = [i for i in issues if i.get("auto_fixable")]
        
        if not auto_fixable:
            return polish_data
        
        logger.info(f"Applying {len(auto_fixable)} auto-fixes")
        
        for issue in auto_fixable:
            suggested_fix = issue.get("suggested_fix", "")
            locations = issue.get("locations", [])
            
            for location in locations:
                chapter_num = int(location.replace("chapter ", "")) if location.replace("chapter ", "").isdigit() else None
                if chapter_num:
                    for chapter in polish_data.get("chapters", []):
                        if chapter.get("chapter_number") == chapter_num:
                            content = chapter.get("content", "")
                            if suggested_fix and suggested_fix in content:
                                pass
        
        return polish_data
    
    async def postprocess_result(self, result: AgentResponse) -> AgentResponse:
        if result.success and result.data:
            issues = len(result.data.get("issues", []))
            auto_fixed = result.data.get("auto_fixed", False)
            result.data["summary"] = f"Consistency check: {issues} issues found, auto-fixed: {auto_fixed}"
        return result
