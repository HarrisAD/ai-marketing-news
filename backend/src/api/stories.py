from fastapi import APIRouter, HTTPException, Query
from typing import List, Optional
from datetime import datetime, timedelta
from models.story import Story
from services.crawler_service import CrawlerService

router = APIRouter(prefix="/api", tags=["stories"])
crawler_service = CrawlerService()

@router.get("/stories")
async def get_stories(
    min_score: Optional[int] = Query(None, ge=0, le=100, description="Minimum marketing relevance score"),
    source_domain: Optional[str] = Query(None, description="Filter by source domain"),
    days_back: Optional[int] = Query(None, ge=1, le=365, description="Number of days back to fetch"),
    limit: Optional[int] = Query(None, ge=1, le=1000, description="Maximum number of stories"),
    canonical_only: bool = Query(True, description="Return only canonical stories (no duplicates)")
):
    """Get stories with optional filtering"""
    try:
        stories = crawler_service.get_stories(
            min_score=min_score,
            source_domain=source_domain,
            days_back=days_back,
            limit=limit
        )
        
        # Filter canonical only if requested
        if canonical_only:
            stories = [s for s in stories if s.get('is_canonical', True)]
        
        return {
            "success": True,
            "stories": stories,
            "count": len(stories),
            "filters": {
                "min_score": min_score,
                "source_domain": source_domain,
                "days_back": days_back,
                "limit": limit,
                "canonical_only": canonical_only
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/stories/{story_id}")
async def get_story(story_id: str):
    """Get a specific story by ID"""
    try:
        story = crawler_service.get_story_by_id(story_id)
        
        if not story:
            raise HTTPException(status_code=404, detail="Story not found")
        
        return {
            "success": True,
            "story": story
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/refresh")
async def refresh_stories(source_domains: Optional[List[str]] = None):
    """Manually trigger news crawling and story updates"""
    try:
        result = crawler_service.run_full_update(source_domains)
        
        if result['success']:
            return {
                "success": True,
                "message": "Stories updated successfully",
                "details": result
            }
        else:
            raise HTTPException(status_code=500, detail=result.get('error', 'Update failed'))
            
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/sources")
async def get_available_sources():
    """Get list of available news sources"""
    try:
        sources = crawler_service.get_available_sources()
        return {
            "success": True,
            "sources": sources,
            "count": len(sources)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/tags")
async def get_available_tags():
    """Get list of available story tags"""
    try:
        tags = crawler_service.get_available_tags()
        return {
            "success": True,
            "tags": tags,
            "count": len(tags)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/stats")
async def get_system_stats():
    """Get system statistics"""
    try:
        stats = crawler_service.get_stats()
        return {
            "success": True,
            "stats": stats
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))