"""
API Router for Story operations.
"""

from fastapi import APIRouter, HTTPException, Depends, status
from typing import List, Optional
import uuid

from app.schemas.story import Story, StoryCreate, StoryUpdate, StoryStatus
from app.schemas.chapter import Chapter, ChapterCreate, ChapterUpdate
from app.schemas.character import Character, CharacterCreate, CharacterUpdate
from app.schemas.pipeline import PipelineState, PipelineStatus
from app.state_machine.pipeline_state_machine import PipelineStateMachine

router = APIRouter()

# In-memory storage (to be replaced with database)
stories_db: dict[str, Story] = {}
chapters_db: dict[str, Chapter] = {}
characters_db: dict[str, Character] = {}
pipelines_db: dict[str, PipelineStateMachine] = {}


@router.get("", response_model=List[Story])
async def get_stories():
    """Get all stories."""
    return list(stories_db.values())


@router.post("", response_model=Story, status_code=status.HTTP_201_CREATED)
async def create_story(story_data: StoryCreate):
    """Create a new story."""
    story_id = str(uuid.uuid4())
    story = Story(
        id=story_id,
        title=story_data.title,
        description=story_data.description,
        genre=story_data.genre,
        tags=story_data.tags or [],
        status=StoryStatus.DRAFT,
        chapter_count=0,
        word_count=0,
    )
    stories_db[story_id] = story
    
    # Initialize pipeline state machine for the story
    pipeline_sm = PipelineStateMachine(story_id=story_id)
    pipelines_db[story_id] = pipeline_sm
    
    return story


@router.get("/{story_id}", response_model=Story)
async def get_story(story_id: str):
    """Get a specific story by ID."""
    if story_id not in stories_db:
        raise HTTPException(status_code=404, detail="Story not found")
    return stories_db[story_id]


@router.put("/{story_id}", response_model=Story)
async def update_story(story_id: str, story_data: StoryUpdate):
    """Update an existing story."""
    if story_id not in stories_db:
        raise HTTPException(status_code=404, detail="Story not found")
    
    story = stories_db[story_id]
    update_data = story_data.model_dump(exclude_unset=True)
    
    for field, value in update_data.items():
        setattr(story, field, value)
    
    stories_db[story_id] = story
    return story


@router.delete("/{story_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_story(story_id: str):
    """Delete a story."""
    if story_id not in stories_db:
        raise HTTPException(status_code=404, detail="Story not found")
    
    del stories_db[story_id]
    # Also delete related chapters, characters, and pipeline
    chapters_to_delete = [cid for cid, ch in chapters_db.items() if ch.story_id == story_id]
    for cid in chapters_to_delete:
        del chapters_db[cid]
    
    characters_to_delete = [cid for cid, ch in characters_db.items() if ch.story_id == story_id]
    for cid in characters_to_delete:
        del characters_db[cid]
    
    if story_id in pipelines_db:
        del pipelines_db[story_id]


# Chapter endpoints
@router.get("/{story_id}/chapters", response_model=List[Chapter])
async def get_chapters(story_id: str):
    """Get all chapters for a story."""
    if story_id not in stories_db:
        raise HTTPException(status_code=404, detail="Story not found")
    
    return [ch for ch in chapters_db.values() if ch.story_id == story_id]


@router.post("/{story_id}/chapters", response_model=Chapter, status_code=status.HTTP_201_CREATED)
async def create_chapter(story_id: str, chapter_data: ChapterCreate):
    """Create a new chapter for a story."""
    if story_id not in stories_db:
        raise HTTPException(status_code=404, detail="Story not found")
    
    chapter_id = str(uuid.uuid4())
    chapter = Chapter(
        id=chapter_id,
        story_id=story_id,
        title=chapter_data.title,
        summary=chapter_data.summary,
        order=chapter_data.order,
        content="",
        word_count=0,
        scene_ids=[],
    )
    chapters_db[chapter_id] = chapter
    
    # Update story chapter count
    story = stories_db[story_id]
    story.chapter_count = len([ch for ch in chapters_db.values() if ch.story_id == story_id])
    
    return chapter


@router.get("/{story_id}/chapters/{chapter_id}", response_model=Chapter)
async def get_chapter(story_id: str, chapter_id: str):
    """Get a specific chapter."""
    if story_id not in stories_db:
        raise HTTPException(status_code=404, detail="Story not found")
    
    chapter = next((ch for ch in chapters_db.values() if ch.id == chapter_id and ch.story_id == story_id), None)
    if not chapter:
        raise HTTPException(status_code=404, detail="Chapter not found")
    
    return chapter


@router.put("/{story_id}/chapters/{chapter_id}", response_model=Chapter)
async def update_chapter(story_id: str, chapter_id: str, chapter_data: ChapterUpdate):
    """Update a chapter."""
    if story_id not in stories_db:
        raise HTTPException(status_code=404, detail="Story not found")
    
    chapter = next((ch for ch in chapters_db.values() if ch.id == chapter_id and ch.story_id == story_id), None)
    if not chapter:
        raise HTTPException(status_code=404, detail="Chapter not found")
    
    update_data = chapter_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(chapter, field, value)
    
    chapters_db[chapter_id] = chapter
    return chapter


@router.delete("/{story_id}/chapters/{chapter_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_chapter(story_id: str, chapter_id: str):
    """Delete a chapter."""
    if story_id not in stories_db:
        raise HTTPException(status_code=404, detail="Story not found")
    
    chapter = next((ch for ch in chapters_db.values() if ch.id == chapter_id and ch.story_id == story_id), None)
    if not chapter:
        raise HTTPException(status_code=404, detail="Chapter not found")
    
    del chapters_db[chapter_id]
    # Update story chapter count
    story = stories_db[story_id]
    story.chapter_count = len([ch for ch in chapters_db.values() if ch.story_id == story_id])


# Character endpoints
@router.get("/{story_id}/characters", response_model=List[Character])
async def get_characters(story_id: str):
    """Get all characters for a story."""
    if story_id not in stories_db:
        raise HTTPException(status_code=404, detail="Story not found")
    
    return [ch for ch in characters_db.values() if ch.story_id == story_id]


@router.post("/{story_id}/characters", response_model=Character, status_code=status.HTTP_201_CREATED)
async def create_character(story_id: str, character_data: CharacterCreate):
    """Create a new character for a story."""
    if story_id not in stories_db:
        raise HTTPException(status_code=404, detail="Story not found")
    
    character_id = str(uuid.uuid4())
    character = Character(
        id=character_id,
        story_id=story_id,
        name=character_data.name,
        description=character_data.description,
        role=character_data.role or "supporting",
        background=character_data.background,
        traits=character_data.traits or [],
        motivations=character_data.motivations or [],
    )
    characters_db[character_id] = character
    return character


@router.put("/{story_id}/characters/{character_id}", response_model=Character)
async def update_character(story_id: str, character_id: str, character_data: CharacterUpdate):
    """Update a character."""
    if story_id not in stories_db:
        raise HTTPException(status_code=404, detail="Story not found")
    
    character = next((ch for ch in characters_db.values() if ch.id == character_id and ch.story_id == story_id), None)
    if not character:
        raise HTTPException(status_code=404, detail="Character not found")
    
    update_data = character_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(character, field, value)
    
    characters_db[character_id] = character
    return character


@router.delete("/{story_id}/characters/{character_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_character(story_id: str, character_id: str):
    """Delete a character."""
    if story_id not in stories_db:
        raise HTTPException(status_code=404, detail="Story not found")
    
    character = next((ch for ch in characters_db.values() if ch.id == character_id and ch.story_id == story_id), None)
    if not character:
        raise HTTPException(status_code=404, detail="Character not found")
    
    del characters_db[character_id]


# Pipeline endpoints
@router.get("/{story_id}/pipeline", response_model=PipelineState)
async def get_pipeline(story_id: str):
    """Get pipeline state for a story."""
    if story_id not in stories_db:
        raise HTTPException(status_code=404, detail="Story not found")
    
    if story_id not in pipelines_db:
        # Create default pipeline state
        pipeline_sm = PipelineStateMachine(story_id=story_id)
        pipelines_db[story_id] = pipeline_sm
    
    pipeline_sm = pipelines_db[story_id]
    status_data = pipeline_sm.get_status()
    
    return PipelineState(
        id=pipeline_sm.pipeline_id,
        story_id=story_id,
        status=PipelineStatus(status_data["status"]),
        current_phase=status_data["current_phase"],
        progress=pipeline_sm.progress,
        config={},
        metadata=pipeline_sm.metadata,
    )


@router.post("/{story_id}/pipeline/start", response_model=PipelineState)
async def start_pipeline(story_id: str, config: Optional[dict] = None):
    """Start the pipeline for a story."""
    if story_id not in stories_db:
        raise HTTPException(status_code=404, detail="Story not found")
    
    if story_id not in pipelines_db:
        pipeline_sm = PipelineStateMachine(story_id=story_id)
        pipelines_db[story_id] = pipeline_sm
    
    pipeline_sm = pipelines_db[story_id]
    pipeline_sm.start()
    
    status_data = pipeline_sm.get_status()
    return PipelineState(
        id=pipeline_sm.pipeline_id,
        story_id=story_id,
        status=PipelineStatus(status_data["status"]),
        current_phase=status_data["current_phase"],
        progress=pipeline_sm.progress,
        config=config or {},
        metadata=pipeline_sm.metadata,
    )


@router.post("/{story_id}/pipeline/pause", response_model=PipelineState)
async def pause_pipeline(story_id: str):
    """Pause the pipeline."""
    if story_id not in stories_db:
        raise HTTPException(status_code=404, detail="Story not found")
    
    if story_id not in pipelines_db:
        raise HTTPException(status_code=404, detail="Pipeline not found")
    
    pipeline_sm = pipelines_db[story_id]
    pipeline_sm.pause()
    
    status_data = pipeline_sm.get_status()
    return PipelineState(
        id=pipeline_sm.pipeline_id,
        story_id=story_id,
        status=PipelineStatus(status_data["status"]),
        current_phase=status_data["current_phase"],
        progress=pipeline_sm.progress,
        config={},
        metadata=pipeline_sm.metadata,
    )


@router.post("/{story_id}/pipeline/resume", response_model=PipelineState)
async def resume_pipeline(story_id: str):
    """Resume the pipeline."""
    if story_id not in stories_db:
        raise HTTPException(status_code=404, detail="Story not found")
    
    if story_id not in pipelines_db:
        raise HTTPException(status_code=404, detail="Pipeline not found")
    
    pipeline_sm = pipelines_db[story_id]
    pipeline_sm.resume_from_pause()
    
    status_data = pipeline_sm.get_status()
    return PipelineState(
        id=pipeline_sm.pipeline_id,
        story_id=story_id,
        status=PipelineStatus(status_data["status"]),
        current_phase=status_data["current_phase"],
        progress=pipeline_sm.progress,
        config={},
        metadata=pipeline_sm.metadata,
    )


@router.post("/{story_id}/pipeline/approve/{phase}", response_model=PipelineState)
async def approve_phase(story_id: str, phase: str):
    """Approve a pipeline phase."""
    if story_id not in stories_db:
        raise HTTPException(status_code=404, detail="Story not found")
    
    if story_id not in pipelines_db:
        raise HTTPException(status_code=404, detail="Pipeline not found")
    
    pipeline_sm = pipelines_db[story_id]
    pipeline_sm.approve_and_continue()
    
    # Trigger next phase transition
    try:
        pipeline_sm.next_phase()
    except Exception:
        pass  # May already be at the end
    
    status_data = pipeline_sm.get_status()
    return PipelineState(
        id=pipeline_sm.pipeline_id,
        story_id=story_id,
        status=PipelineStatus(status_data["status"]),
        current_phase=status_data["current_phase"],
        progress=pipeline_sm.progress,
        config={},
        metadata=pipeline_sm.metadata,
    )


@router.post("/{story_id}/pipeline/reject/{phase}", response_model=PipelineState)
async def reject_phase(story_id: str, phase: str, reason: dict):
    """Reject a pipeline phase."""
    if story_id not in stories_db:
        raise HTTPException(status_code=404, detail="Story not found")
    
    if story_id not in pipelines_db:
        raise HTTPException(status_code=404, detail="Pipeline not found")
    
    pipeline_sm = pipelines_db[story_id]
    reason_text = reason.get("reason", "No reason provided")
    pipeline_sm.reject_and_revision()
    
    status_data = pipeline_sm.get_status()
    return PipelineState(
        id=pipeline_sm.pipeline_id,
        story_id=story_id,
        status=PipelineStatus(status_data["status"]),
        current_phase=status_data["current_phase"],
        progress=pipeline_sm.progress,
        config={},
        metadata={**pipeline_sm.metadata, "rejection_reason": reason_text},
    )
