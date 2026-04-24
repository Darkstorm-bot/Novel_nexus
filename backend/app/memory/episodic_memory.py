"""
Episodic memory store for specific events and occurrences.
"""

from typing import List, Dict, Any, Optional
from datetime import datetime
import uuid
import json

from app.core.logging_config import get_logger
from app.schemas.memory import EpisodicMemory, MemoryType

logger = get_logger(__name__)


class EpisodicMemoryStore:
    """Store for episodic memories - specific events in the narrative."""
    
    def __init__(self):
        self._memories: Dict[str, EpisodicMemory] = {}
        self._story_index: Dict[str, List[str]] = {}  # story_id -> memory_ids
        self._chapter_index: Dict[str, List[str]] = {}  # chapter_id -> memory_ids
    
    async def add_memory(
        self,
        content: str,
        story_id: str,
        event_type: Optional[str] = None,
        chapter_id: Optional[str] = None,
        scene_id: Optional[str] = None,
        participants: Optional[List[str]] = None,
        metadata: Optional[Dict[str, Any]] = None,
        importance: float = 0.5,
    ) -> str:
        """Add an episodic memory."""
        memory_id = str(uuid.uuid4())
        
        memory = EpisodicMemory(
            id=memory_id,
            type=MemoryType.EPISODIC,
            content=content,
            story_id=story_id,
            event_type=event_type,
            chapter_id=chapter_id,
            scene_id=scene_id,
            participants=participants or [],
            metadata=metadata or {},
            importance=importance,
            timestamp=datetime.utcnow(),
        )
        
        self._memories[memory_id] = memory
        
        # Index by story
        if story_id not in self._story_index:
            self._story_index[story_id] = []
        self._story_index[story_id].append(memory_id)
        
        # Index by chapter
        if chapter_id:
            if chapter_id not in self._chapter_index:
                self._chapter_index[chapter_id] = []
            self._chapter_index[chapter_id].append(memory_id)
        
        logger.debug("Episodic memory added", memory_id=memory_id, event_type=event_type)
        return memory_id
    
    async def get_memory(self, memory_id: str) -> Optional[EpisodicMemory]:
        """Get a specific episodic memory."""
        return self._memories.get(memory_id)
    
    async def get_memories_by_story(
        self,
        story_id: str,
        event_type: Optional[str] = None,
        limit: int = 50,
    ) -> List[EpisodicMemory]:
        """Get episodic memories for a story."""
        memory_ids = self._story_index.get(story_id, [])
        memories = []
        
        for mid in memory_ids[-limit:]:  # Most recent first
            memory = self._memories.get(mid)
            if memory:
                if event_type is None or memory.event_type == event_type:
                    memories.append(memory)
        
        return memories
    
    async def get_memories_by_chapter(
        self,
        chapter_id: str,
    ) -> List[EpisodicMemory]:
        """Get episodic memories for a chapter."""
        memory_ids = self._chapter_index.get(chapter_id, [])
        memories = []
        
        for mid in memory_ids:
            memory = self._memories.get(mid)
            if memory:
                memories.append(memory)
        
        return memories
    
    async def get_memories_by_participant(
        self,
        participant: str,
        story_id: Optional[str] = None,
        limit: int = 50,
    ) -> List[EpisodicMemory]:
        """Get episodic memories involving a specific participant."""
        memories = []
        
        for memory in self._memories.values():
            if story_id and memory.story_id != story_id:
                continue
            if participant in memory.participants:
                memories.append(memory)
                if len(memories) >= limit:
                    break
        
        # Sort by timestamp (most recent first)
        memories.sort(key=lambda m: m.timestamp or datetime.min, reverse=True)
        return memories
    
    async def update_memory(
        self,
        memory_id: str,
        **kwargs,
    ) -> Optional[EpisodicMemory]:
        """Update an episodic memory."""
        memory = self._memories.get(memory_id)
        if not memory:
            return None
        
        for key, value in kwargs.items():
            if hasattr(memory, key):
                setattr(memory, key, value)
        
        memory.updated_at = datetime.utcnow()
        logger.debug("Episodic memory updated", memory_id=memory_id)
        return memory
    
    async def delete_memory(self, memory_id: str) -> bool:
        """Delete an episodic memory."""
        memory = self._memories.get(memory_id)
        if not memory:
            return False
        
        # Remove from indexes
        if memory.story_id in self._story_index:
            try:
                self._story_index[memory.story_id].remove(memory_id)
            except ValueError:
                pass
        
        if memory.chapter_id and memory.chapter_id in self._chapter_index:
            try:
                self._chapter_index[memory.chapter_id].remove(memory_id)
            except ValueError:
                pass
        
        del self._memories[memory_id]
        logger.debug("Episodic memory deleted", memory_id=memory_id)
        return True
    
    async def search_memories(
        self,
        story_id: str,
        query_terms: Optional[List[str]] = None,
        event_types: Optional[List[str]] = None,
        participants: Optional[List[str]] = None,
        limit: int = 20,
    ) -> List[EpisodicMemory]:
        """Search episodic memories with filters."""
        memories = await self.get_memories_by_story(story_id, limit=1000)
        results = []
        
        for memory in memories:
            # Filter by event type
            if event_types and memory.event_type not in event_types:
                continue
            
            # Filter by participants
            if participants and not any(p in memory.participants for p in participants):
                continue
            
            # Filter by query terms
            if query_terms:
                content_lower = memory.content.lower()
                if not any(term.lower() in content_lower for term in query_terms):
                    continue
            
            results.append(memory)
            
            if len(results) >= limit:
                break
        
        return results
    
    async def clear_story_memories(self, story_id: str) -> int:
        """Clear all episodic memories for a story."""
        memory_ids = self._story_index.get(story_id, []).copy()
        count = 0
        
        for memory_id in memory_ids:
            if await self.delete_memory(memory_id):
                count += 1
        
        logger.info("Cleared episodic memories", story_id=story_id, count=count)
        return count
    
    async def export_memories(self, story_id: str) -> List[Dict[str, Any]]:
        """Export episodic memories for a story."""
        memories = await self.get_memories_by_story(story_id)
        return [memory.model_dump() for memory in memories]
    
    async def import_memories(
        self,
        story_id: str,
        memories_data: List[Dict[str, Any]],
    ) -> List[str]:
        """Import episodic memories for a story."""
        memory_ids = []
        
        for data in memories_data:
            memory_id = await self.add_memory(
                content=data.get("content", ""),
                story_id=story_id,
                event_type=data.get("event_type"),
                chapter_id=data.get("chapter_id"),
                scene_id=data.get("scene_id"),
                participants=data.get("participants", []),
                metadata=data.get("metadata", {}),
                importance=data.get("importance", 0.5),
            )
            memory_ids.append(memory_id)
        
        logger.info("Imported episodic memories", story_id=story_id, count=len(memory_ids))
        return memory_ids
