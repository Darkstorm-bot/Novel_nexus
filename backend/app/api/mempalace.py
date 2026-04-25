"""
MemPalace API Routes for Narrative Nexus V4.0

Provides REST endpoints for:
- LLM provider connection testing
- Memory storage and retrieval
- Story consistency checking
- Entity extraction
"""

from fastapi import APIRouter, HTTPException, BackgroundTasks
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field

from app.services.mempalace_service import (
    get_mempalace_service,
    initialize_mempalace_service,
    MemPalaceConnectionConfig,
    mempalace_transaction
)

router = APIRouter(prefix="/mempalace", tags=["MemPalace"])


class LLMTestRequest(BaseModel):
    """Request to test LLM connection"""
    provider: str = Field(default="openai-compat", description="LLM provider name")
    model: str = Field(default="local-model", description="Model name")
    endpoint: Optional[str] = Field(default="http://localhost:1234/v1", description="API endpoint URL")
    api_key: Optional[str] = Field(default=None, description="API key")
    timeout: int = Field(default=120, description="Request timeout in seconds")


class LLMTestResponse(BaseModel):
    """Response from LLM connection test"""
    success: bool
    message: str
    provider_info: Optional[Dict[str, Any]] = None


class MemoryStoreRequest(BaseModel):
    """Request to store a memory"""
    collection_name: str = Field(..., description="Collection name (e.g., 'story_123')")
    content: str = Field(..., description="Content to store")
    metadata: Optional[Dict[str, Any]] = Field(default=None, description="Optional metadata")


class MemoryStoreResponse(BaseModel):
    """Response from memory storage"""
    success: bool
    message: str


class MemorySearchRequest(BaseModel):
    """Request to search memories"""
    collection_name: str = Field(..., description="Collection name to search")
    query: str = Field(..., description="Search query")
    n_results: int = Field(default=5, description="Number of results to return")


class MemorySearchResponse(BaseModel):
    """Response from memory search"""
    success: bool
    results: List[Dict[str, Any]]


class ConsistencyCheckRequest(BaseModel):
    """Request to check story consistency"""
    story_id: str = Field(..., description="Story ID")
    new_content: str = Field(..., description="New content to check")
    context: Optional[str] = Field(default=None, description="Additional context")


class ConsistencyCheckResponse(BaseModel):
    """Response from consistency check"""
    success: bool
    report: Dict[str, Any]


class EntityExtractionRequest(BaseModel):
    """Request to extract entities from content"""
    story_id: str = Field(..., description="Story ID")
    content: str = Field(..., description="Content to analyze")


class EntityExtractionResponse(BaseModel):
    """Response from entity extraction"""
    success: bool
    entities: Dict[str, List[str]]


@router.post("/initialize", response_model=Dict[str, Any])
async def initialize_mempalace(config: Optional[LLMTestRequest] = None):
    """
    Initialize or reinitialize MemPalace service.
    
    This endpoint sets up the connection to the LLM provider and ChromaDB.
    """
    if config:
        mempalace_config = MemPalaceConnectionConfig(
            llm_provider=config.provider,
            llm_model=config.model,
            llm_endpoint=config.endpoint,
            llm_api_key=config.api_key,
            chroma_path="./mempalace_data",
            timeout=config.timeout
        )
        success, message = await initialize_mempalace_service(mempalace_config)
    else:
        success, message = await initialize_mempalace_service()
    
    if not success:
        raise HTTPException(status_code=500, detail=message)
    
    return {"success": True, "message": message}


@router.post("/test-llm", response_model=LLMTestResponse)
async def test_llm_connection(request: LLMTestRequest):
    """
    Test connection to an LLM provider.
    
    Useful for debugging LM Studio, Ollama, or other provider connections.
    """
    try:
        config = MemPalaceConnectionConfig(
            llm_provider=request.provider,
            llm_model=request.model,
            llm_endpoint=request.endpoint,
            llm_api_key=request.api_key,
            timeout=request.timeout
        )
        
        service = get_mempalace_service()
        if not service:
            # Create temporary service for testing
            from app.services.mempalace_service import MemPalaceService
            temp_service = MemPalaceService(config)
            await temp_service.initialize()
            provider = temp_service.get_llm_provider()
        else:
            # Reconfigure existing service
            await initialize_mempalace_service(config)
            service = get_mempalace_service()
            provider = service.get_llm_provider() if service else None
        
        if not provider:
            return LLMTestResponse(
                success=False,
                message="Failed to create LLM provider"
            )
        
        available, message = provider.check_available()
        
        return LLMTestResponse(
            success=available,
            message=message,
            provider_info={
                "name": provider.name,
                "model": provider.model,
                "endpoint": provider.endpoint
            }
        )
        
    except Exception as e:
        return LLMTestResponse(
            success=False,
            message=f"Connection test failed: {str(e)}"
        )


@router.post("/memory/store", response_model=MemoryStoreResponse)
async def store_memory(request: MemoryStoreRequest):
    """
    Store a memory in the specified collection.
    
    Memories are used for long-term story consistency and character tracking.
    """
    service = get_mempalace_service()
    if not service or not service.is_initialized():
        raise HTTPException(status_code=503, detail="MemPalace service not initialized")
    
    success, message = await service.store_memory(
        collection_name=request.collection_name,
        content=request.content,
        metadata=request.metadata
    )
    
    if not success:
        raise HTTPException(status_code=500, detail=message)
    
    return MemoryStoreResponse(success=True, message=message)


@router.post("/memory/search", response_model=MemorySearchResponse)
async def search_memories(request: MemorySearchRequest):
    """
    Search for memories in a collection.
    
    Uses semantic search to find relevant story elements.
    """
    service = get_mempalace_service()
    if not service or not service.is_initialized():
        raise HTTPException(status_code=503, detail="MemPalace service not initialized")
    
    success, results = await service.search_memories(
        collection_name=request.collection_name,
        query=request.query,
        n_results=request.n_results
    )
    
    if not success:
        raise HTTPException(status_code=500, detail="Search failed")
    
    return MemorySearchResponse(success=True, results=results)


@router.post("/consistency/check", response_model=ConsistencyCheckResponse)
async def check_consistency(request: ConsistencyCheckRequest):
    """
    Check story consistency using MemPalace memory.
    
    Analyzes new content against existing story memories to identify:
    - Character contradictions
    - Plot inconsistencies
    - Timeline errors
    - Setting discrepancies
    """
    service = get_mempalace_service()
    if not service or not service.is_initialized():
        raise HTTPException(status_code=503, detail="MemPalace service not initialized")
    
    success, report = await service.check_consistency(
        story_id=request.story_id,
        new_content=request.new_content,
        context=request.context
    )
    
    if not success:
        raise HTTPException(status_code=500, detail=report.get("error", "Consistency check failed"))
    
    return ConsistencyCheckResponse(success=True, report=report)


@router.post("/entities/extract", response_model=EntityExtractionResponse)
async def extract_entities(request: EntityExtractionRequest):
    """
    Extract named entities from story content.
    
    Identifies and categorizes:
    - Characters
    - Locations
    - Objects
    - Organizations
    
    Automatically stores extracted entities in memory.
    """
    service = get_mempalace_service()
    if not service or not service.is_initialized():
        raise HTTPException(status_code=503, detail="MemPalace service not initialized")
    
    success, entities = await service.extract_entities(
        story_id=request.story_id,
        content=request.content
    )
    
    if not success:
        raise HTTPException(status_code=500, detail=entities.get("error", "Entity extraction failed"))
    
    return EntityExtractionResponse(success=True, entities=entities)


@router.get("/status")
async def get_mempalace_status():
    """
    Get MemPalace service status.
    
    Returns information about:
    - Service initialization state
    - Configured LLM provider
    - ChromaDB connection
    """
    service = get_mempalace_service()
    
    if not service:
        return {
            "initialized": False,
            "message": "Service not initialized"
        }
    
    provider = service.get_llm_provider()
    provider_info = None
    if provider:
        available, message = provider.check_available()
        provider_info = {
            "name": provider.name,
            "model": provider.model,
            "endpoint": provider.endpoint,
            "available": available,
            "status": message
        }
    
    return {
        "initialized": service.is_initialized(),
        "config": {
            "llm_provider": service.config.llm_provider,
            "llm_model": service.config.llm_model,
            "chroma_path": service.config.chroma_path
        },
        "provider": provider_info
    }


@router.post("/debug/connection")
async def debug_connection(request: LLMTestRequest):
    """
    Debug connection issues with LLM providers.
    
    Provides detailed diagnostic information for troubleshooting:
    - Network connectivity
    - Authentication
    - Model availability
    - Response format validation
    """
    diagnostics = {
        "provider": request.provider,
        "model": request.model,
        "endpoint": request.endpoint,
        "steps": []
    }
    
    try:
        # Step 1: Validate endpoint URL
        diagnostics["steps"].append({
            "step": "URL Validation",
            "status": "pass" if request.endpoint else "fail",
            "details": f"Endpoint: {request.endpoint or 'Not provided'}"
        })
        
        if not request.endpoint:
            diagnostics["error"] = "No endpoint provided"
            return diagnostics
        
        # Step 2: Create provider
        try:
            config = MemPalaceConnectionConfig(
                llm_provider=request.provider,
                llm_model=request.model,
                llm_endpoint=request.endpoint,
                llm_api_key=request.api_key,
                timeout=min(request.timeout, 10)  # Short timeout for diagnostics
            )
            
            from app.services.mempalace_service import MemPalaceService
            temp_service = MemPalaceService(config)
            await temp_service.initialize()
            provider = temp_service.get_llm_provider()
            
            diagnostics["steps"].append({
                "step": "Provider Creation",
                "status": "pass",
                "details": f"Created {provider.name} provider"
            })
        except Exception as e:
            diagnostics["steps"].append({
                "step": "Provider Creation",
                "status": "fail",
                "details": str(e)
            })
            diagnostics["error"] = f"Failed to create provider: {str(e)}"
            return diagnostics
        
        # Step 3: Check availability
        try:
            available, message = provider.check_available()
            diagnostics["steps"].append({
                "step": "Availability Check",
                "status": "pass" if available else "fail",
                "details": message
            })
        except Exception as e:
            diagnostics["steps"].append({
                "step": "Availability Check",
                "status": "fail",
                "details": str(e)
            })
        
        # Step 4: Test simple query
        try:
            success, response = await temp_service.query_llm(
                system_prompt="You are a test assistant. Respond with 'OK'.",
                user_prompt="Test",
                json_mode=False
            )
            diagnostics["steps"].append({
                "step": "Query Test",
                "status": "pass" if success else "fail",
                "details": response[:100] if success else response
            })
        except Exception as e:
            diagnostics["steps"].append({
                "step": "Query Test",
                "status": "fail",
                "details": str(e)
            })
        
        diagnostics["overall_status"] = "healthy" if all(
            s["status"] == "pass" for s in diagnostics["steps"]
        ) else "unhealthy"
        
    except Exception as e:
        diagnostics["error"] = f"Diagnostic failed: {str(e)}"
        diagnostics["overall_status"] = "error"
    
    return diagnostics
