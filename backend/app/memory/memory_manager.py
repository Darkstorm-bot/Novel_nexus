"""
Memory Manager - Orchestrates the three-layer memory system.
"""

from typing import List, Dict, Any, Optional
from datetime import datetime

from app.core.logging_config import get_logger
from app.schemas.memory import MemoryType, VectorMemory
from app.memory.vector_store import VectorStore, ChromaVectorStore
from app.memory.episodic_memory import EpisodicMemoryStore
from app.memory.working_memory import WorkingMemoryStore
from config.settings import settings

logger = get_logger(__name__)


class MemoryManager:
    """
    Manages the three-layer memory system:
    - Vector Memory: Semantic search and retrieval
    - Episodic Memory: Specific events and occurrences
    - Working Memory: Active context for ongoing operations
    """
    
    def __init__(self):
        self.vector_store: Optional[VectorStore] = None
        self.episodic_store: Optional[EpisodicMemoryStore] = None
        self.working_store: Optional[WorkingMemoryStore] = None
        self._initialized = False
    
    async def initialize(self) -> None:
        """Initialize all memory stores."""
        if self._initialized:
            return
        
        try:
            # Initialize vector store
            self.vector_store = ChromaVectorStore()
            await self.vector_store.initialize()
            
            # Initialize episodic memory store
            self.episodic_store = EpisodicMemoryStore()
            
            # Initialize working memory store
            self.working_store = WorkingMemoryStore()
            
            self._initialized = True
            logger.info("Memory manager initialized successfully")
            
        except Exception as e:
            logger.error("Failed to initialize memory manager", error=str(e))
            raise
    
    async def close(self) -> None:
        """Close all memory stores."""
        if self.vector_store:
            await self.vector_store.close()
        self._initialized = False
        logger.info("Memory manager closed")
    
    # Vector Memory Operations
    
    async def store_in_vector_memory(
        self,
        content: str,
        story_id: str,
        memory_type: MemoryType = MemoryType.VECTOR,
        metadata: Optional[Dict[str, Any]] = None,
        importance: float = 0.5,
    ) -> str:
        """Store content in vector memory."""
        if not self._initialized:
            await self.initialize()
        
        meta = metadata or {}
        meta.update({
            "story_id": story_id,
            "memory_type": memory_type.value,
            "importance": importance,
            "created_at": datetime.utcnow().isoformat(),
        })
        
        doc_id = await self.vector_store.add_document(
            document=content,
            metadata=meta,
        )
        
        logger.debug("Content stored in vector memory", document_id=doc_id)
        return doc_id
    
    async def search_vector_memory(
        self,
        query: str,
        story_id: Optional[str] = None,
        memory_type: Optional[MemoryType] = None,
        top_k: int = 5,
        min_importance: float = 0.0,
    ) -> List[Dict[str, Any]]:
        """Search vector memory with optional filters."""
        if not self._initialized:
            await self.initialize()
        
        filters = {}
        if story_id:
            filters["story_id"] = story_id
        if memory_type:
            filters["memory_type"] = memory_type.value
        if min_importance > 0:
            filters["importance"] = {"$gte": min_importance}
        
        results = await self.vector_store.search(
            query=query,
            top_k=top_k,
            filters=filters if filters else None,
        )
        
        logger.debug("Vector memory search completed", results_count=len(results))
        return results
    
    # Episodic Memory Operations
    
    async def store_episodic_memory(
        self,
        content: str,
        story_id: str,
        event_type: Optional[str] = None,
        chapter_id: Optional[str] = None,
        scene_id: Optional[str] = None,
        participants: Optional[List[str]] = None,
        importance: float = 0.5,
    ) -> str:
        """Store an episodic memory."""
        if not self._initialized:
            await self.initialize()
        
        memory_id = await self.episodic_store.add_memory(
            content=content,
            story_id=story_id,
            event_type=event_type,
            chapter_id=chapter_id,
            scene_id=scene_id,
            participants=participants,
            importance=importance,
        )
        
        # Also store in vector memory for semantic search
        await self.store_in_vector_memory(
            content=content,
            story_id=story_id,
            memory_type=MemoryType.EPISODIC,
            metadata={
                "event_type": event_type,
                "chapter_id": chapter_id,
                "scene_id": scene_id,
                "episodic_memory_id": memory_id,
            },
            importance=importance,
        )
        
        return memory_id
    
    async def get_episodic_memories(
        self,
        story_id: str,
        event_type: Optional[str] = None,
        limit: int = 50,
    ) -> List[Any]:
        """Get episodic memories for a story."""
        if not self._initialized:
            await self.initialize()
        
        return await self.episodic_store.get_memories_by_story(
            story_id=story_id,
            event_type=event_type,
            limit=limit,
        )
    
    # Working Memory Operations
    
    async def get_working_memory(self, story_id: str) -> Optional[Any]:
        """Get working memory for a story."""
        if not self._initialized:
            await self.initialize()
        
        return await self.working_store.create_or_get(story_id)
    
    async def update_working_memory(
        self,
        story_id: str,
        **kwargs,
    ) -> Optional[Any]:
        """Update working memory for a story."""
        if not self._initialized:
            await self.initialize()
        
        return await self.working_store.update_context(story_id, **kwargs)
    
    # Unified Search
    
    async def search_all_memories(
        self,
        query: str,
        story_id: str,
        top_k: int = 10,
    ) -> Dict[str, List[Dict[str, Any]]]:
        """Search across all memory layers."""
        if not self._initialized:
            await self.initialize()
        
        results = {
            "vector": [],
            "episodic": [],
            "working": [],
        }
        
        # Search vector memory
        vector_results = await self.search_vector_memory(
            query=query,
            story_id=story_id,
            top_k=top_k,
        )
        results["vector"] = vector_results
        
        # Search episodic memory
        episodic_results = await self.episodic_store.search_memories(
            story_id=story_id,
            query_terms=[query],
            limit=top_k,
        )
        results["episodic"] = [r.model_dump() for r in episodic_results]
        
        # Get working memory context
        working_memory = await self.working_store.get(story_id)
        if working_memory:
            results["working"] = [working_memory.model_dump()]
        
        logger.debug("Multi-layer memory search completed")
        return results
    
    # Character State Tracking Integration
    
    async def track_character_appearance(
        self,
        character_id: str,
        story_id: str,
        chapter_id: Optional[str] = None,
        scene_id: Optional[str] = None,
        context: Optional[str] = None,
    ) -> None:
        """Track a character appearance in memory."""
        if not self._initialized:
            await self.initialize()
        
        # Add to working memory
        await self.working_store.add_active_character(story_id, character_id)
        
        # Store episodic memory of appearance
        if context:
            await self.store_episodic_memory(
                content=context,
                story_id=story_id,
                event_type="character_appearance",
                chapter_id=chapter_id,
                scene_id=scene_id,
                participants=[character_id],
            )
        
        logger.debug("Character appearance tracked", character_id=character_id)
    
    async def get_relevant_context(
        self,
        story_id: str,
        query: str,
        include_characters: bool = True,
        top_k: int = 5,
    ) -> Dict[str, Any]:
        """Get relevant context for LLM operations."""
        if not self._initialized:
            await self.initialize()
        
        context = {
            "vector_memories": [],
            "episodic_memories": [],
            "working_memory": None,
            "active_characters": [],
        }
        
        # Get vector memories
        context["vector_memories"] = await self.search_vector_memory(
            query=query,
            story_id=story_id,
            top_k=top_k,
        )
        
        # Get recent episodic memories
        context["episodic_memories"] = await self.get_episodic_memories(
            story_id=story_id,
            limit=top_k,
        )
        
        # Get working memory
        working_memory = await self.working_store.get(story_id)
        if working_memory:
            context["working_memory"] = working_memory.model_dump()
            if include_characters:
                context["active_characters"] = working_memory.active_characters
        
        return context
