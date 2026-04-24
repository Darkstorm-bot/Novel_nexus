# Application Settings
from pydantic_settings import BaseSettings
from typing import Optional, List


class Settings(BaseSettings):
    """Application configuration settings."""
    
    # App Info
    APP_NAME: str = "Narrative Nexus"
    APP_VERSION: str = "4.0.0"
    DEBUG: bool = True
    
    # Server
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    
    # LLM Configuration
    LLM_PROVIDER: str = "ollama"
    LLM_MODEL: str = "llama2"
    LLM_BASE_URL: Optional[str] = "http://localhost:11434"
    LLM_API_KEY: Optional[str] = None
    
    # Vector Database
    CHROMA_PERSIST_DIR: str = "./chroma_db"
    CHROMA_COLLECTION_NAME: str = "narrative_nexus"
    
    # Memory System
    MEMORY_TOP_K: int = 5
    MEMORY_SIMILARITY_THRESHOLD: float = 0.7
    
    # WebSocket
    WS_HEARTBEAT_INTERVAL: int = 30
    
    # CORS
    CORS_ORIGINS: List[str] = ["http://localhost:3000", "http://localhost:5173"]
    
    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()
