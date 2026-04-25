"""
MemPalace Integration Service for Narrative Nexus V4.0

MemPalace is a memory system that gives AI long-term memory capabilities.
It uses ChromaDB for vector storage and supports multiple LLM providers:
- OpenAI-compatible endpoints (LM Studio, Ollama, etc.)
- Ollama local models
- Anthropic Claude

This service integrates MemPalace as the primary database for novel storage,
providing:
- Long-term memory for story consistency
- Character and plot tracking across sessions
- Semantic search for story elements
- Automatic deduplication and entity extraction
"""

import os
import logging
from typing import Optional, Dict, Any, List, Tuple
from dataclasses import dataclass
from contextlib import asynccontextmanager

from mempalace.llm_client import get_provider, LLMProvider, LLMResponse, LLMError
from mempalace.palace import get_collection, ChromaBackend
from mempalace.config import MempalaceConfig

logger = logging.getLogger(__name__)


@dataclass
class MemPalaceConnectionConfig:
    """Configuration for MemPalace connection"""
    llm_provider: str = "openai-compat"  # openai-compat, ollama, anthropic
    llm_model: str = "local-model"
    llm_endpoint: Optional[str] = "http://localhost:1234/v1"
    llm_api_key: Optional[str] = None
    chroma_path: str = "./mempalace_data"
    timeout: int = 120


class MemPalaceService:
    """
    Service class for integrating MemPalace memory system with Narrative Nexus.
    
    Provides methods for:
    - Connecting to LLM providers (LM Studio, Ollama, etc.)
    - Storing and retrieving story memories
    - Character and plot consistency checking
    - Semantic search across story elements
    """
    
    def __init__(self, config: MemPalaceConnectionConfig):
        self.config = config
        self._llm_provider: Optional[LLMProvider] = None
        self._chroma_backend: Optional[ChromaBackend] = None
        self._initialized = False
        
    async def initialize(self) -> Tuple[bool, str]:
        """
        Initialize MemPalace service with LLM provider and ChromaDB.
        
        Returns:
            Tuple of (success: bool, message: str)
        """
        try:
            logger.info(f"Initializing MemPalace with provider: {self.config.llm_provider}")
            
            # Initialize LLM provider
            self._llm_provider = get_provider(
                name=self.config.llm_provider,
                model=self.config.llm_model,
                endpoint=self.config.llm_endpoint,
                api_key=self.config.llm_api_key or os.environ.get("OPENAI_API_KEY"),
                timeout=self.config.timeout
            )
            
            # Check if LLM provider is available
            available, message = self._llm_provider.check_available()
            if not available:
                logger.warning(f"LLM provider not available: {message}")
                # Continue anyway - some features may still work
            
            # Initialize ChromaDB backend
            os.makedirs(self.config.chroma_path, exist_ok=True)
            self._chroma_backend = ChromaBackend(persist_directory=self.config.chroma_path)
            
            self._initialized = True
            logger.info("MemPalace initialized successfully")
            return True, "MemPalace initialized successfully"
            
        except Exception as e:
            error_msg = f"Failed to initialize MemPalace: {str(e)}"
            logger.error(error_msg, exc_info=True)
            return False, error_msg
    
    def is_initialized(self) -> bool:
        """Check if service is initialized"""
        return self._initialized
    
    def get_llm_provider(self) -> Optional[LLMProvider]:
        """Get the configured LLM provider"""
        return self._llm_provider
    
    async def store_memory(
        self,
        collection_name: str,
        content: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Tuple[bool, str]:
        """
        Store a memory in the specified collection.
        
        Args:
            collection_name: Name of the collection (e.g., 'story_123', 'characters')
            content: The text content to store
            metadata: Optional metadata dictionary
            
        Returns:
            Tuple of (success: bool, message: str)
        """
        if not self._initialized:
            return False, "MemPalace not initialized"
        
        try:
            collection = get_collection(
                name=collection_name,
                backend=self._chroma_backend
            )
            
            # Add document to collection
            collection.add(
                documents=[content],
                metadatas=[metadata or {}],
                ids=[f"mem_{len(collection.get()['ids'])}"]
            )
            
            logger.info(f"Stored memory in collection '{collection_name}'")
            return True, "Memory stored successfully"
            
        except Exception as e:
            error_msg = f"Failed to store memory: {str(e)}"
            logger.error(error_msg, exc_info=True)
            return False, error_msg
    
    async def search_memories(
        self,
        collection_name: str,
        query: str,
        n_results: int = 5
    ) -> Tuple[bool, List[Dict[str, Any]]]:
        """
        Search for memories in a collection.
        
        Args:
            collection_name: Name of the collection to search
            query: Search query text
            n_results: Number of results to return
            
        Returns:
            Tuple of (success: bool, results: list)
        """
        if not self._initialized:
            return False, []
        
        try:
            collection = get_collection(
                name=collection_name,
                backend=self._chroma_backend
            )
            
            results = collection.query(
                query_texts=[query],
                n_results=n_results
            )
            
            # Format results
            formatted_results = []
            if results['documents'] and results['documents'][0]:
                for i, doc in enumerate(results['documents'][0]):
                    formatted_results.append({
                        'content': doc,
                        'metadata': results['metadatas'][0][i] if results['metadatas'] else {},
                        'distance': results['distances'][0][i] if results['distances'] else None
                    })
            
            return True, formatted_results
            
        except Exception as e:
            error_msg = f"Failed to search memories: {str(e)}"
            logger.error(error_msg, exc_info=True)
            return False, []
    
    async def query_llm(
        self,
        system_prompt: str,
        user_prompt: str,
        json_mode: bool = True
    ) -> Tuple[bool, str]:
        """
        Query the configured LLM provider.
        
        Args:
            system_prompt: System instruction prompt
            user_prompt: User query prompt
            json_mode: Whether to request JSON response
            
        Returns:
            Tuple of (success: bool, response: str)
        """
        if not self._llm_provider:
            return False, "LLM provider not configured"
        
        try:
            response: LLMResponse = self._llm_provider.classify(
                system=system_prompt,
                user=user_prompt,
                json_mode=json_mode
            )
            
            return True, response.text
            
        except LLMError as e:
            error_msg = f"LLM error: {str(e)}"
            logger.error(error_msg)
            return False, error_msg
        except Exception as e:
            error_msg = f"Failed to query LLM: {str(e)}"
            logger.error(error_msg, exc_info=True)
            return False, error_msg
    
    async def check_consistency(
        self,
        story_id: str,
        new_content: str,
        context: Optional[str] = None
    ) -> Tuple[bool, Dict[str, Any]]:
        """
        Check story consistency using MemPalace memory.
        
        Args:
            story_id: ID of the story
            new_content: New content to check
            context: Optional additional context
            
        Returns:
            Tuple of (success: bool, consistency_report: dict)
        """
        if not self._initialized:
            return False, {"error": "MemPalace not initialized"}
        
        try:
            # Search for relevant memories
            success, memories = await self.search_memories(
                collection_name=f"story_{story_id}",
                query=new_content[:500],  # Use first 500 chars for search
                n_results=10
            )
            
            if not success:
                return False, {"error": "Failed to retrieve memories"}
            
            # Build context from memories
            memory_context = "\n".join([m['content'] for m in memories])
            
            # Query LLM for consistency check
            system_prompt = """You are a story consistency checker. 
            Analyze the new content against the existing story memory.
            Identify any contradictions in:
            - Character traits, names, or backgrounds
            - Plot points and timeline
            - Setting details
            - Established facts
            
            Return a JSON object with:
            {
                "consistent": boolean,
                "issues": [{"type": string, "description": string, "severity": "low|medium|high"}],
                "suggestions": [string]
            }"""
            
            user_prompt = f"""Existing story memory:
{memory_context}

New content to check:
{new_content}

Additional context: {context or 'None'}

Provide consistency analysis."""
            
            success, response = await self.query_llm(
                system_prompt=system_prompt,
                user_prompt=user_prompt,
                json_mode=True
            )
            
            if not success:
                return False, {"error": response}
            
            # Parse JSON response (basic parsing)
            import json
            try:
                report = json.loads(response)
                return True, report
            except json.JSONDecodeError:
                return True, {"raw_response": response, "parsed": False}
                
        except Exception as e:
            error_msg = f"Consistency check failed: {str(e)}"
            logger.error(error_msg, exc_info=True)
            return False, {"error": error_msg}
    
    async def extract_entities(
        self,
        story_id: str,
        content: str
    ) -> Tuple[bool, Dict[str, List[str]]]:
        """
        Extract entities (characters, locations, objects) from content.
        
        Args:
            story_id: ID of the story
            content: Content to analyze
            
        Returns:
            Tuple of (success: bool, entities: dict)
        """
        if not self._llm_provider:
            return False, {"error": "LLM provider not configured"}
        
        try:
            system_prompt = """Extract all named entities from the text.
            Categorize them into: characters, locations, objects, organizations.
            Return a JSON object with arrays for each category."""
            
            user_prompt = f"Extract entities from this story content:\n\n{content}"
            
            success, response = await self.query_llm(
                system_prompt=system_prompt,
                user_prompt=user_prompt,
                json_mode=True
            )
            
            if not success:
                return False, {"error": response}
            
            import json
            try:
                entities = json.loads(response)
                
                # Store extracted entities in memory
                for category, items in entities.items():
                    for item in items:
                        await self.store_memory(
                            collection_name=f"story_{story_id}_entities",
                            content=f"{category}: {item}",
                            metadata={"category": category, "entity": item}
                        )
                
                return True, entities
            except json.JSONDecodeError:
                return True, {"raw_response": response, "parsed": False}
                
        except Exception as e:
            error_msg = f"Entity extraction failed: {str(e)}"
            logger.error(error_msg, exc_info=True)
            return False, {"error": error_msg}


# Global service instance
_mempalace_service: Optional[MemPalaceService] = None


def get_mempalace_service() -> Optional[MemPalaceService]:
    """Get the global MemPalace service instance"""
    return _mempalace_service


async def initialize_mempalace_service(config: Optional[MemPalaceConnectionConfig] = None) -> Tuple[bool, str]:
    """
    Initialize the global MemPalace service.
    
    Args:
        config: Optional configuration. If not provided, uses environment variables.
        
    Returns:
        Tuple of (success: bool, message: str)
    """
    global _mempalace_service
    
    if config is None:
        config = MemPalaceConnectionConfig(
            llm_provider=os.environ.get("MEMPALACE_LLM_PROVIDER", "openai-compat"),
            llm_model=os.environ.get("MEMPALACE_LLM_MODEL", "local-model"),
            llm_endpoint=os.environ.get("MEMPALACE_LLM_ENDPOINT", "http://localhost:1234/v1"),
            llm_api_key=os.environ.get("MEMPALACE_LLM_API_KEY"),
            chroma_path=os.environ.get("MEMPALACE_CHROMA_PATH", "./mempalace_data"),
            timeout=int(os.environ.get("MEMPALACE_TIMEOUT", "120"))
        )
    
    _mempalace_service = MemPalaceService(config)
    return await _mempalace_service.initialize()


@asynccontextmanager
async def mempalace_transaction(collection_name: str):
    """
    Context manager for MemPalace transactions.
    
    Usage:
        async with mempalace_transaction("story_123") as service:
            await service.store_memory(content="...")
    """
    service = get_mempalace_service()
    if not service or not service.is_initialized():
        raise RuntimeError("MemPalace service not initialized")
    
    yield service
