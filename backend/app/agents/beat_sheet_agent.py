"""
Beat Sheet Creation Agent - Phase 3 of the pipeline.
Creates detailed beat sheets based on approved outlines.
"""

from typing import Dict, Any, List
import json

from app.agents.base_agent import BaseAgent, AgentResponse
from app.core.logging_config import get_logger

logger = get_logger(__name__)


class BeatSheetCreationAgent(BaseAgent):
    """
    Agent responsible for creating beat sheets.
    
    Tasks:
    - Define scene-by-scene beats
    - Map emotional arcs
    - Identify tension points
    - Plan pacing
    """
    
    def __init__(self):
        super().__init__("BeatSheetCreationAgent")
    
    async def execute(
        self,
        story_id: str,
        context: Dict[str, Any],
    ) -> AgentResponse:
        """Execute beat sheet creation."""
        try:
            logger.info("Starting beat sheet creation", story_id=story_id)
            
            outline_data = context.get("outline_data", {})
            if not outline_data:
                return self._create_response(
                    success=False,
                    errors=["No outline data provided."],
                )
            
            system_prompt = self._build_system_prompt()
            prompt = self._build_beat_sheet_prompt(outline_data, context)
            
            llm_response = await self._get_llm_response(prompt, system_prompt)
            beat_data = self._parse_beat_response(llm_response)
            
            required_fields = ["beats", "scene_breakdown"]
            errors = await self._validate_output(beat_data, required_fields)
            
            if errors:
                return self._create_response(success=False, errors=errors)
            
            await self._store_beat_memory(story_id, beat_data, context)
            
            return self._create_response(
                success=True,
                data=beat_data,
                requires_approval=True,
                metadata={"phase": "beat_sheet", "beats_generated": True}
            )
            
        except Exception as e:
            logger.error("Beat sheet creation failed", story_id=story_id, error=str(e))
            return self._create_response(success=False, errors=[str(e)])
    
    def _build_system_prompt(self) -> str:
        return """You are an expert story structurer specializing in beat sheets.
Create a detailed beat sheet with scene-by-scene breakdown.

Format as JSON:
{
    "beats": [
        {
            "beat_number": 1,
            "chapter": 1,
            "type": "action|emotion|revelation",
            "description": "string",
            "characters_involved": [],
            "tension_level": 1-10
        }
    ],
    "scene_breakdown": [
        {
            "scene_number": 1,
            "chapter": 1,
            "location": "string",
            "pov_character": "string",
            "goal": "string",
            "conflict": "string",
            "outcome": "string"
        }
    ],
    "emotional_arc": {"character": ["emotion sequence"]},
    "pacing_notes": "string"
}"""
    
    def _build_beat_sheet_prompt(
        self,
        outline_data: Dict[str, Any],
        context: Dict[str, Any],
    ) -> str:
        chapter_outline = outline_data.get("chapter_outline", [])
        plot_points = outline_data.get("plot_points", [])
        
        return f"""Based on this outline, create a detailed beat sheet:

CHAPTERS: {len(chapter_outline)}
PLOT POINTS: {len(plot_points)}

Create scene-by-scene beats with emotional arcs and pacing."""
    
    def _parse_beat_response(self, response: str) -> Dict[str, Any]:
        try:
            start_idx = response.find("{")
            end_idx = response.rfind("}") + 1
            if start_idx >= 0 and end_idx > start_idx:
                return json.loads(response[start_idx:end_idx])
        except json.JSONDecodeError:
            pass
        return {"beats": [], "scene_breakdown": [], "emotional_arc": {}, "pacing_notes": ""}
    
    async def _store_beat_memory(
        self,
        story_id: str,
        beat_data: Dict[str, Any],
        context: Dict[str, Any],
    ) -> None:
        memory_manager = context.get("memory_manager")
        if not memory_manager:
            return
        
        from app.schemas.memory import MemoryType
        
        for beat in beat_data.get("beats", []):
            await memory_manager.store_in_vector_memory(
                content=beat.get("description", ""),
                story_id=story_id,
                memory_type=MemoryType.PLOT,
                metadata={"element": "beat", "beat_number": beat.get("beat_number")},
                importance=0.6,
            )
    
    async def postprocess_result(self, result: AgentResponse) -> AgentResponse:
        if result.success and result.data:
            beat_count = len(result.data.get("beats", []))
            result.data["summary"] = f"Generated {beat_count} beats"
        return result
