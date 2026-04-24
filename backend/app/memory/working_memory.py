"""
Working memory store for active context and short-term information.
"""

from typing import List, Dict, Any, Optional
from datetime import datetime
import uuid

from app.core.logging_config import get_logger
from app.schemas.memory import WorkingMemory

logger = get_logger(__name__)


class WorkingMemoryStore:
    """Store for working memory - active context for ongoing operations."""
    
    def __init__(self):
        self._memories: Dict[str, WorkingMemory] = {}
        self._story_index: Dict[str, str] = {}  # story_id -> memory_id (one per story)
    
    async def create_or_get(
        self,
        story_id: str,
    ) -> WorkingMemory:
        """Create a new working memory or get existing one for a story."""
        if story_id in self._story_index:
            memory_id = self._story_index[story_id]
            if memory_id in self._memories:
                return self._memories[memory_id]
        
        # Create new working memory
        memory_id = str(uuid.uuid4())
        memory = WorkingMemory(
            id=memory_id,
            story_id=story_id,
        )
        
        self._memories[memory_id] = memory
        self._story_index[story_id] = memory_id
        
        logger.debug("Working memory created", story_id=story_id)
        return memory
    
    async def get(self, story_id: str) -> Optional[WorkingMemory]:
        """Get working memory for a story."""
        memory_id = self._story_index.get(story_id)
        if memory_id:
            return self._memories.get(memory_id)
        return None
    
    async def update_context(
        self,
        story_id: str,
        active_characters: Optional[List[str]] = None,
        current_plot_threads: Optional[List[str]] = None,
        recent_events: Optional[List[str]] = None,
        open_questions: Optional[List[str]] = None,
        context_window: Optional[Dict[str, Any]] = None,
    ) -> Optional[WorkingMemory]:
        """Update working memory context."""
        memory = await self.create_or_get(story_id)
        
        if active_characters is not None:
            memory.active_characters = active_characters
        if current_plot_threads is not None:
            memory.current_plot_threads = current_plot_threads
        if recent_events is not None:
            memory.recent_events = recent_events
        if open_questions is not None:
            memory.open_questions = open_questions
        if context_window is not None:
            memory.context_window.update(context_window)
        
        memory.updated_at = datetime.utcnow()
        logger.debug("Working memory updated", story_id=story_id)
        return memory
    
    async def add_active_character(
        self,
        story_id: str,
        character_id: str,
    ) -> Optional[WorkingMemory]:
        """Add a character to active characters list."""
        memory = await self.create_or_get(story_id)
        
        if character_id not in memory.active_characters:
            memory.active_characters.append(character_id)
            memory.updated_at = datetime.utcnow()
            logger.debug("Character added to working memory", character_id=character_id)
        
        return memory
    
    async def remove_active_character(
        self,
        story_id: str,
        character_id: str,
    ) -> Optional[WorkingMemory]:
        """Remove a character from active characters list."""
        memory = await self.get(story_id)
        if not memory:
            return None
        
        if character_id in memory.active_characters:
            memory.active_characters.remove(character_id)
            memory.updated_at = datetime.utcnow()
            logger.debug("Character removed from working memory", character_id=character_id)
        
        return memory
    
    async def add_recent_event(
        self,
        story_id: str,
        event: str,
        max_events: int = 10,
    ) -> Optional[WorkingMemory]:
        """Add a recent event to working memory."""
        memory = await self.create_or_get(story_id)
        
        memory.recent_events.append(event)
        
        # Keep only the most recent events
        if len(memory.recent_events) > max_events:
            memory.recent_events = memory.recent_events[-max_events:]
        
        memory.updated_at = datetime.utcnow()
        logger.debug("Recent event added to working memory")
        return memory
    
    async def add_open_question(
        self,
        story_id: str,
        question: str,
    ) -> Optional[WorkingMemory]:
        """Add an open question to working memory."""
        memory = await self.create_or_get(story_id)
        
        if question not in memory.open_questions:
            memory.open_questions.append(question)
            memory.updated_at = datetime.utcnow()
            logger.debug("Open question added to working memory")
        
        return memory
    
    async def resolve_question(
        self,
        story_id: str,
        question: str,
    ) -> Optional[WorkingMemory]:
        """Mark a question as resolved."""
        memory = await self.get(story_id)
        if not memory:
            return None
        
        if question in memory.open_questions:
            memory.open_questions.remove(question)
            memory.updated_at = datetime.utcnow()
            logger.debug("Question resolved in working memory")
        
        return memory
    
    async def clear(self, story_id: str) -> bool:
        """Clear working memory for a story."""
        memory_id = self._story_index.get(story_id)
        if not memory_id:
            return False
        
        if memory_id in self._memories:
            del self._memories[memory_id]
        del self._story_index[story_id]
        
        logger.debug("Working memory cleared", story_id=story_id)
        return True
    
    async def get_context_summary(self, story_id: str) -> Dict[str, Any]:
        """Get a summary of the working memory context."""
        memory = await self.get(story_id)
        if not memory:
            return {}
        
        return {
            "active_characters_count": len(memory.active_characters),
            "active_characters": memory.active_characters,
            "plot_threads_count": len(memory.current_plot_threads),
            "recent_events_count": len(memory.recent_events),
            "open_questions_count": len(memory.open_questions),
            "context_window_keys": list(memory.context_window.keys()),
        }
