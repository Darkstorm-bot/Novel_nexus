"""
ID generation utilities for Narrative Nexus.
"""

import uuid
from datetime import datetime


def generate_id(prefix: str = "") -> str:
    """Generate a unique ID with optional prefix."""
    unique_id = str(uuid.uuid4())
    if prefix:
        return f"{prefix}_{unique_id}"
    return unique_id


def generate_story_id() -> str:
    """Generate a unique story ID."""
    timestamp = datetime.utcnow().strftime("%Y%m%d")
    unique_id = uuid.uuid4().hex[:8]
    return f"story_{timestamp}_{unique_id}"


def generate_chapter_id(story_id: str) -> str:
    """Generate a unique chapter ID linked to a story."""
    unique_id = uuid.uuid4().hex[:6]
    return f"{story_id}_ch_{unique_id}"


def generate_scene_id(chapter_id: str) -> str:
    """Generate a unique scene ID linked to a chapter."""
    unique_id = uuid.uuid4().hex[:6]
    return f"{chapter_id}_sc_{unique_id}"


def generate_character_id(story_id: str) -> str:
    """Generate a unique character ID linked to a story."""
    unique_id = uuid.uuid4().hex[:6]
    return f"{story_id}_char_{unique_id}"
