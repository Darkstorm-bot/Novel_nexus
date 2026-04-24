"""
Concept Development Agent - Phase 1 of the pipeline.
Generates story concepts, themes, and core ideas.
"""

from typing import Dict, Any, Optional, List
import json

from app.agents.base_agent import BaseAgent, AgentResponse
from app.core.logging_config import get_logger

logger = get_logger(__name__)


class ConceptDevelopmentAgent(BaseAgent):
    """
    Agent responsible for developing story concepts.
    
    Tasks:
    - Generate story premise and logline
    - Define core themes and motifs
    - Establish tone and style
    - Create initial world-building elements
    - Identify target audience
    """
    
    def __init__(self):
        super().__init__("ConceptDevelopmentAgent")
    
    async def execute(
        self,
        story_id: str,
        context: Dict[str, Any],
    ) -> AgentResponse:
        """Execute concept development."""
        try:
            logger.info("Starting concept development", story_id=story_id)
            
            # Extract input parameters
            user_input = context.get("user_input", "")
            genre = context.get("genre", "")
            preferences = context.get("preferences", {})
            
            # Build the prompt for concept generation
            system_prompt = self._build_system_prompt()
            prompt = self._build_concept_prompt(user_input, genre, preferences)
            
            # Get LLM response
            llm_response = await self._get_llm_response(prompt, system_prompt)
            
            # Parse the concept data
            concept_data = self._parse_concept_response(llm_response)
            
            # Validate the output
            required_fields = ["premise", "logline", "themes", "tone"]
            errors = await self._validate_output(concept_data, required_fields)
            
            if errors:
                return self._create_response(
                    success=False,
                    errors=errors,
                )
            
            # Store concept in memory
            await self._store_concept_memory(story_id, concept_data, context)
            
            return self._create_response(
                success=True,
                data=concept_data,
                requires_approval=True,
                metadata={
                    "phase": "concept",
                    "concept_generated": True,
                }
            )
            
        except Exception as e:
            logger.error("Concept development failed", story_id=story_id, error=str(e))
            return self._create_response(
                success=False,
                errors=[str(e)],
            )
    
    def _build_system_prompt(self) -> str:
        """Build the system prompt for concept generation."""
        return """You are an expert story developer specializing in creating compelling narrative concepts.
Your task is to generate a comprehensive story concept including:
- A unique and engaging premise
- A concise logline (1-2 sentences)
- Core themes and motifs
- Tone and style guidelines
- Basic world-building elements
- Target audience identification

Format your response as valid JSON with these fields:
{
    "premise": "string",
    "logline": "string", 
    "themes": ["list of themes"],
    "motifs": ["list of motifs"],
    "tone": "string",
    "style": "string",
    "world_building": {"key": "value"},
    "target_audience": "string"
}"""
    
    def _build_concept_prompt(
        self,
        user_input: str,
        genre: str,
        preferences: Dict[str, Any],
    ) -> str:
        """Build the user prompt for concept generation."""
        prompt_parts = []
        
        if user_input:
            prompt_parts.append(f"User's initial idea: {user_input}")
        
        if genre:
            prompt_parts.append(f"Genre: {genre}")
        
        if preferences:
            prefs_str = ", ".join(f"{k}: {v}" for k, v in preferences.items())
            prompt_parts.append(f"Preferences: {prefs_str}")
        
        base_prompt = "Develop a comprehensive story concept based on the following:"
        return f"{base_prompt}\n\n" + "\n".join(prompt_parts)
    
    def _parse_concept_response(self, response: str) -> Dict[str, Any]:
        """Parse the LLM response into structured concept data."""
        try:
            # Try to extract JSON from response
            start_idx = response.find("{")
            end_idx = response.rfind("}") + 1
            
            if start_idx >= 0 and end_idx > start_idx:
                json_str = response[start_idx:end_idx]
                concept_data = json.loads(json_str)
            else:
                # Fallback parsing for non-JSON responses
                concept_data = self._fallback_parse(response)
            
            return concept_data
            
        except json.JSONDecodeError:
            logger.warning("Failed to parse JSON, using fallback")
            return self._fallback_parse(response)
    
    def _fallback_parse(self, response: str) -> Dict[str, Any]:
        """Fallback parsing for non-JSON responses."""
        lines = response.strip().split("\n")
        concept_data = {
            "premise": "",
            "logline": "",
            "themes": [],
            "motifs": [],
            "tone": "neutral",
            "style": "narrative",
            "world_building": {},
            "target_audience": "general",
        }
        
        current_field = None
        current_list = []
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
            
            if line.startswith("Premise:") or line.startswith("**Premise:**"):
                concept_data["premise"] = line.split(":", 1)[-1].strip()
            elif line.startswith("Logline:") or line.startswith("**Logline:**"):
                concept_data["logline"] = line.split(":", 1)[-1].strip()
            elif line.startswith("Themes:") or line.startswith("**Themes:**"):
                current_field = "themes"
            elif line.startswith("Tone:") or line.startswith("**Tone:**"):
                concept_data["tone"] = line.split(":", 1)[-1].strip()
        
        return concept_data
    
    async def _store_concept_memory(
        self,
        story_id: str,
        concept_data: Dict[str, Any],
        context: Dict[str, Any],
    ) -> None:
        """Store concept in vector memory for future reference."""
        from app.memory import MemoryManager
        
        memory_manager = context.get("memory_manager")
        if not memory_manager:
            return
        
        # Store premise in vector memory
        premise = concept_data.get("premise", "")
        if premise:
            await memory_manager.store_in_vector_memory(
                content=premise,
                story_id=story_id,
                memory_type=type('obj', (object,), {'VECTOR': 'vector'})(),
                metadata={"concept_element": "premise"},
                importance=0.9,
            )
        
        # Store themes
        themes = concept_data.get("themes", [])
        for theme in themes:
            await memory_manager.store_in_vector_memory(
                content=f"Theme: {theme}",
                story_id=story_id,
                memory_type=type('obj', (object,), {'VECTOR': 'vector'})(),
                metadata={"concept_element": "theme"},
                importance=0.7,
            )
    
    async def preprocess_context(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Preprocess context before execution."""
        # Ensure required fields exist
        if "user_input" not in context:
            context["user_input"] = ""
        if "genre" not in context:
            context["genre"] = "general fiction"
        if "preferences" not in context:
            context["preferences"] = {}
        
        return context
    
    async def postprocess_result(self, result: AgentResponse) -> AgentResponse:
        """Postprocess result after execution."""
        if result.success and result.data:
            # Add summary for display
            result.data["summary"] = (
                f"Generated concept: {result.data.get('logline', 'No logline')} "
                f"with themes: {', '.join(result.data.get('themes', [])[:3])}"
            )
        
        return result
