"""
Draft Writing Agent - Phase 4 of the pipeline.
Writes first draft based on approved beat sheets.
"""

from typing import Dict, Any, List
import json

from app.agents.base_agent import BaseAgent, AgentResponse
from app.core.logging_config import get_logger

logger = get_logger(__name__)


class DraftWritingAgent(BaseAgent):
    """
    Agent responsible for writing first drafts.
    
    Tasks:
    - Write scene content
    - Develop dialogue
    - Create descriptions
    - Maintain voice and tone
    """
    
    def __init__(self):
        super().__init__("DraftWritingAgent")
    
    async def execute(
        self,
        story_id: str,
        context: Dict[str, Any],
    ) -> AgentResponse:
        try:
            logger.info("Starting draft writing", story_id=story_id)
            
            beat_data = context.get("beat_data", {})
            if not beat_data:
                return self._create_response(
                    success=False,
                    errors=["No beat data provided."],
                )
            
            system_prompt = self._build_system_prompt()
            prompt = self._build_draft_prompt(beat_data, context)
            
            llm_response = await self._get_llm_response(prompt, system_prompt)
            draft_data = self._parse_draft_response(llm_response)
            
            required_fields = ["chapters", "content"]
            errors = await self._validate_output(draft_data, required_fields)
            
            if errors:
                return self._create_response(success=False, errors=errors)
            
            await self._store_draft_memory(story_id, draft_data, context)
            
            return self._create_response(
                success=True,
                data=draft_data,
                requires_approval=True,
                metadata={"phase": "drafting", "draft_written": True}
            )
            
        except Exception as e:
            logger.error("Draft writing failed", story_id=story_id, error=str(e))
            return self._create_response(success=False, errors=[str(e)])
    
    def _build_system_prompt(self) -> str:
        return """You are an expert fiction writer. Write compelling narrative prose.
Format as JSON:
{
    "chapters": [
        {
            "chapter_number": 1,
            "title": "string",
            "content": "full chapter text",
            "word_count": 0,
            "scenes": [
                {
                    "scene_number": 1,
                    "content": "scene text"
                }
            ]
        }
    ],
    "total_word_count": 0,
    "writing_notes": "string"
}"""
    
    def _build_draft_prompt(
        self,
        beat_data: Dict[str, Any],
        context: Dict[str, Any],
    ) -> str:
        beats = beat_data.get("beats", [])
        return f"Write a full draft based on these {len(beats)} beats. Include dialogue, description, and action."
    
    def _parse_draft_response(self, response: str) -> Dict[str, Any]:
        try:
            start_idx = response.find("{")
            end_idx = response.rfind("}") + 1
            if start_idx >= 0 and end_idx > start_idx:
                return json.loads(response[start_idx:end_idx])
        except json.JSONDecodeError:
            pass
        return {"chapters": [], "content": "", "total_word_count": 0}
    
    async def _store_draft_memory(
        self,
        story_id: str,
        draft_data: Dict[str, Any],
        context: Dict[str, Any],
    ) -> None:
        memory_manager = context.get("memory_manager")
        if not memory_manager:
            return
        
        from app.schemas.memory import MemoryType
        
        for chapter in draft_data.get("chapters", []):
            content = chapter.get("content", "")
            if content:
                await memory_manager.store_in_vector_memory(
                    content=content[:5000],  # Truncate for storage
                    story_id=story_id,
                    memory_type=MemoryType.VECTOR,
                    metadata={"element": "draft", "chapter": chapter.get("chapter_number")},
                    importance=0.9,
                )
    
    async def postprocess_result(self, result: AgentResponse) -> AgentResponse:
        if result.success and result.data:
            word_count = result.data.get("total_word_count", 0)
            result.data["summary"] = f"Draft complete: {word_count} words"
        return result
