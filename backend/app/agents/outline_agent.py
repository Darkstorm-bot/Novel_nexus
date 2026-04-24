"""
Outline Generation Agent - Phase 2 of the pipeline.
Creates detailed story outlines based on approved concepts.
"""

from typing import Dict, Any, List
import json

from app.agents.base_agent import BaseAgent, AgentResponse
from app.core.logging_config import get_logger

logger = get_logger(__name__)


class OutlineGenerationAgent(BaseAgent):
    """
    Agent responsible for generating story outlines.
    
    Tasks:
    - Create act structure (3-act or alternative)
    - Define major plot points
    - Outline chapter breakdown
    - Establish character arcs
    - Map subplots
    """
    
    def __init__(self):
        super().__init__("OutlineGenerationAgent")
    
    async def execute(
        self,
        story_id: str,
        context: Dict[str, Any],
    ) -> AgentResponse:
        """Execute outline generation."""
        try:
            logger.info("Starting outline generation", story_id=story_id)
            
            # Get approved concept data
            concept_data = context.get("concept_data", {})
            if not concept_data:
                return self._create_response(
                    success=False,
                    errors=["No concept data provided. Concept phase must be completed first."],
                )
            
            # Build prompts
            system_prompt = self._build_system_prompt()
            prompt = self._build_outline_prompt(concept_data, context)
            
            # Get LLM response
            llm_response = await self._get_llm_response(prompt, system_prompt)
            
            # Parse outline data
            outline_data = self._parse_outline_response(llm_response)
            
            # Validate output
            required_fields = ["acts", "plot_points", "chapter_outline"]
            errors = await self._validate_output(outline_data, required_fields)
            
            if errors:
                return self._create_response(success=False, errors=errors)
            
            # Store outline in memory
            await self._store_outline_memory(story_id, outline_data, context)
            
            return self._create_response(
                success=True,
                data=outline_data,
                requires_approval=True,
                metadata={"phase": "outline", "outline_generated": True}
            )
            
        except Exception as e:
            logger.error("Outline generation failed", story_id=story_id, error=str(e))
            return self._create_response(success=False, errors=[str(e)])
    
    def _build_system_prompt(self) -> str:
        """Build system prompt for outline generation."""
        return """You are an expert story architect specializing in creating detailed narrative outlines.
Your task is to generate a comprehensive story outline including:
- Act structure (typically 3 acts)
- Major plot points (inciting incident, midpoint, climax, etc.)
- Chapter-by-chapter breakdown
- Character arc progression
- Subplot integration

Format your response as valid JSON with these fields:
{
    "structure_type": "three_act",
    "acts": [
        {
            "act_number": 1,
            "title": "string",
            "summary": "string",
            "chapters": [1, 2, 3]
        }
    ],
    "plot_points": [
        {
            "name": "Inciting Incident",
            "description": "string",
            "act": 1,
            "chapter": 2
        }
    ],
    "chapter_outline": [
        {
            "chapter_number": 1,
            "title": "string",
            "summary": "string",
            "key_events": ["list"],
            "character_focus": ["list"]
        }
    ],
    "character_arcs": {"character": "arc description"},
    "subplots": [{"name": "string", "description": "string"}]
}"""
    
    def _build_outline_prompt(
        self,
        concept_data: Dict[str, Any],
        context: Dict[str, Any],
    ) -> str:
        """Build user prompt for outline generation."""
        premise = concept_data.get("premise", "No premise provided")
        themes = concept_data.get("themes", [])
        tone = concept_data.get("tone", "neutral")
        
        prompt = f"""Based on the following approved concept, create a detailed story outline:

PREMISE: {premise}
THEMES: {', '.join(themes)}
TONE: {tone}

Additional context: {context.get('user_preferences', '')}

Create a comprehensive outline with act structure, major plot points, and chapter breakdown."""
        
        return prompt
    
    def _parse_outline_response(self, response: str) -> Dict[str, Any]:
        """Parse LLM response into structured outline data."""
        try:
            start_idx = response.find("{")
            end_idx = response.rfind("}") + 1
            
            if start_idx >= 0 and end_idx > start_idx:
                json_str = response[start_idx:end_idx]
                outline_data = json.loads(json_str)
            else:
                outline_data = self._fallback_parse(response)
            
            return outline_data
        except json.JSONDecodeError:
            logger.warning("Failed to parse JSON, using fallback")
            return self._fallback_parse(response)
    
    def _fallback_parse(self, response: str) -> Dict[str, Any]:
        """Fallback parsing for non-JSON responses."""
        return {
            "structure_type": "three_act",
            "acts": [],
            "plot_points": [],
            "chapter_outline": [],
            "character_arcs": {},
            "subplots": [],
        }
    
    async def _store_outline_memory(
        self,
        story_id: str,
        outline_data: Dict[str, Any],
        context: Dict[str, Any],
    ) -> None:
        """Store outline in vector memory."""
        from app.schemas.memory import MemoryType
        
        memory_manager = context.get("memory_manager")
        if not memory_manager:
            return
        
        # Store chapter summaries
        chapter_outline = outline_data.get("chapter_outline", [])
        for chapter in chapter_outline:
            summary = chapter.get("summary", "")
            if summary:
                await memory_manager.store_in_vector_memory(
                    content=summary,
                    story_id=story_id,
                    memory_type=MemoryType.PLOT,
                    metadata={
                        "outline_element": "chapter",
                        "chapter_number": chapter.get("chapter_number"),
                    },
                    importance=0.8,
                )
    
    async def postprocess_result(self, result: AgentResponse) -> AgentResponse:
        """Postprocess result."""
        if result.success and result.data:
            chapter_count = len(result.data.get("chapter_outline", []))
            result.data["summary"] = f"Generated outline with {chapter_count} chapters"
        
        return result
