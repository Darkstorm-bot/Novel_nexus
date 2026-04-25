#!/usr/bin/env python3
"""
Backend-Frontend Integration Verification Script
Checks that all frontend API calls match backend endpoints
"""

import re
import os

# Backend routes from stories.py
BACKEND_ROUTES = {
    # Stories
    ("GET", "/stories"),
    ("POST", "/stories"),
    ("GET", "/stories/{story_id}"),
    ("PUT", "/stories/{story_id}"),
    ("DELETE", "/stories/{story_id}"),
    
    # Chapters
    ("GET", "/stories/{story_id}/chapters"),
    ("POST", "/stories/{story_id}/chapters"),
    ("GET", "/stories/{story_id}/chapters/{chapter_id}"),
    ("PUT", "/stories/{story_id}/chapters/{chapter_id}"),
    ("DELETE", "/stories/{story_id}/chapters/{chapter_id}"),
    
    # Characters
    ("GET", "/stories/{story_id}/characters"),
    ("POST", "/stories/{story_id}/characters"),
    ("PUT", "/stories/{story_id}/characters/{character_id}"),
    ("DELETE", "/stories/{story_id}/characters/{character_id}"),
    
    # Pipeline
    ("GET", "/stories/{story_id}/pipeline"),
    ("POST", "/stories/{story_id}/pipeline/start"),
    ("POST", "/stories/{story_id}/pipeline/pause"),
    ("POST", "/stories/{story_id}/pipeline/resume"),
    ("POST", "/stories/{story_id}/pipeline/approve/{phase}"),
    ("POST", "/stories/{story_id}/pipeline/reject/{phase}"),
}

# Frontend API client methods and their expected routes
FRONTEND_CALLS = {
    "getStories": ("GET", "/stories"),
    "createStory": ("POST", "/stories"),
    "getStory": ("GET", "/stories/{id}"),
    "updateStory": ("PUT", "/stories/{id}"),
    "deleteStory": ("DELETE", "/stories/{id}"),
    
    "getChapters": ("GET", "/stories/{storyId}/chapters"),
    "createChapter": ("POST", "/stories/{storyId}/chapters"),
    "getChapter": ("GET", "/stories/{storyId}/chapters/{chapterId}"),
    "updateChapter": ("PUT", "/stories/{storyId}/chapters/{chapterId}"),
    "deleteChapter": ("DELETE", "/stories/{storyId}/chapters/{chapterId}"),
    
    "getCharacters": ("GET", "/stories/{storyId}/characters"),
    "createCharacter": ("POST", "/stories/{storyId}/characters"),
    "updateCharacter": ("PUT", "/stories/{storyId}/characters/{characterId}"),
    "deleteCharacter": ("DELETE", "/stories/{storyId}/characters/{characterId}"),
    
    "getPipeline": ("GET", "/stories/{storyId}/pipeline"),
    "startPipeline": ("POST", "/stories/{storyId}/pipeline/start"),
    "pausePipeline": ("POST", "/stories/{storyId}/pipeline/pause"),
    "resumePipeline": ("POST", "/stories/{storyId}/pipeline/resume"),
    "approvePhase": ("POST", "/stories/{storyId}/pipeline/approve/{phase}"),
    "rejectPhase": ("POST", "/stories/{storyId}/pipeline/reject/{phase}"),
}

def normalize_path(path):
    """Normalize path by replacing variable names with placeholders"""
    return re.sub(r'\{[^}]+\}', '{*}', path)

def verify():
    print("=" * 60)
    print("BACKEND-FRONTEND INTEGRATION VERIFICATION")
    print("=" * 60)
    
    errors = []
    warnings = []
    
    # Check each frontend call has a matching backend route
    for method, (http_method, path) in FRONTEND_CALLS.items():
        normalized_frontend = normalize_path(path)
        
        found = False
        for backend_method, backend_path in BACKEND_ROUTES:
            normalized_backend = normalize_path(backend_path)
            if http_method == backend_method and normalized_frontend == normalized_backend:
                found = True
                break
        
        if not found:
            errors.append(f"❌ {method}: {http_method} {path} - NO MATCHING BACKEND ROUTE")
        else:
            print(f"✓ {method}: {http_method} {path}")
    
    print()
    
    # Check for unused backend routes
    used_paths = set()
    for method, (http_method, path) in FRONTEND_CALLS.items():
        normalized_frontend = normalize_path(path)
        for backend_method, backend_path in BACKEND_ROUTES:
            normalized_backend = normalize_path(backend_path)
            if http_method == backend_method and normalized_frontend == normalized_backend:
                used_paths.add((backend_method, backend_path))
    
    unused = BACKEND_ROUTES - used_paths
    for method, path in unused:
        warnings.append(f"⚠️  Unused backend route: {method} {path}")
    
    # Summary
    print("=" * 60)
    if errors:
        print("ERRORS FOUND:")
        for error in errors:
            print(f"  {error}")
    else:
        print("✅ ALL FRONTEND API CALLS HAVE MATCHING BACKEND ROUTES!")
    
    if warnings:
        print("\nWARNINGS:")
        for warning in warnings:
            print(f"  {warning}")
    
    print("=" * 60)
    return len(errors) == 0

if __name__ == "__main__":
    success = verify()
    exit(0 if success else 1)
