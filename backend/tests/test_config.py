"""
Configuration tests for Narrative Nexus.
"""

import pytest
from config.settings import settings


def test_settings_loaded():
    """Test that settings are loaded correctly."""
    assert settings.APP_NAME == "Narrative Nexus"
    assert settings.APP_VERSION == "4.0.0"
    assert settings.PORT == 8000


def test_settings_chroma_config():
    """Test ChromaDB configuration."""
    assert settings.CHROMA_COLLECTION_NAME == "narrative_nexus"
    assert settings.CHROMA_PERSIST_DIR == "./chroma_db"


def test_settings_memory_config():
    """Test memory system configuration."""
    assert settings.MEMORY_TOP_K == 5
    assert settings.MEMORY_SIMILARITY_THRESHOLD == 0.7
