import logging
import threading
from datetime import datetime
from fastapi import APIRouter, HTTPException, Query, BackgroundTasks
from typing import List, Optional
from pydantic import BaseModel
from models.story import Story
from services.crawler_service import CrawlerService
from services.source_config import source_config

router = APIRouter(prefix="/api", tags=["stories"])
crawler_service = CrawlerService()
logger = logging.getLogger(__name__)

_refresh_lock = threading.Lock()
_refresh_state = {
    "running": False,
    "last_result": None
}


class SourceStatusUpdate(BaseModel):
    active: bool


class SourceCreateRequest(BaseModel):
    domain: str
    name: str
    rss_urls: List[str] = []
    fallback_urls: List[str] = []
    activate: bool = True


class StoriesDeleteRequest(BaseModel):
    story_ids: List[str] = []


def _run_refresh_task():
    """Run the full update and track status for background execution."""
    try:
        result = crawler_service.run_full_update()
        _refresh_state["last_result"] = result
        if result.get("success"):
            logger.info("Stories refresh completed in background")
        else:
            logger.error("Stories refresh completed with errors: %s", result.get("error"))
    except Exception as exc:  # pragma: no cover - defensive logging
        logger.exception("Stories refresh failed in background: %s", exc)
        _refresh_state["last_result"] = {
            "success": False,
            "error": str(exc)
        }
    finally:
        with _refresh_lock:
            _refresh_state["running"] = False

def _parse_date_param(value: Optional[str], end_of_day: bool = False) -> Optional[datetime]:
    """Parse YYYY-MM-DD or ISO datetime strings into datetime objects."""
    if not value:
        return None

    try:
        sanitized = value.replace('Z', '+00:00')
        if 'T' in sanitized:
            return datetime.fromisoformat(sanitized)

        suffix = "T23:59:59.999999" if end_of_day else "T00:00:00"
        return datetime.fromisoformat(f"{sanitized}{suffix}")
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=f"Invalid date format: {value}") from exc


@router.get("/stories")
async def get_stories(
    min_score: Optional[int] = Query(None, ge=0, le=100, description="Minimum marketing relevance score"),
    source_domain: Optional[str] = Query(None, description="Filter by source domain"),
    days_back: Optional[int] = Query(None, ge=1, le=365, description="Number of days back to fetch"),
    limit: Optional[int] = Query(None, ge=1, le=1000, description="Maximum number of stories"),
    canonical_only: bool = Query(True, description="Return only canonical stories (no duplicates)"),
    date_from: Optional[str] = Query(None, description="ISO date (YYYY-MM-DD) or datetime to filter from"),
    date_to: Optional[str] = Query(None, description="ISO date (YYYY-MM-DD) or datetime to filter to")
):
    """Get stories with optional filtering"""
    try:
        parsed_date_from = _parse_date_param(date_from) if date_from else None
        parsed_date_to = _parse_date_param(date_to, end_of_day=True) if date_to else None

        stories = crawler_service.get_stories(
            min_score=min_score,
            source_domain=source_domain,
            days_back=days_back,
            limit=limit,
            date_from=parsed_date_from,
            date_to=parsed_date_to
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
async def refresh_stories(background_tasks: BackgroundTasks):
    """Manually trigger news crawling and story updates"""

    with _refresh_lock:
        if _refresh_state["running"]:
            return {
                "success": True,
                "message": "Stories refresh already running in background",
                "is_background": True,
                "refreshing": True,
                "last_result": _refresh_state.get("last_result")
            }
        _refresh_state["running"] = True

    background_tasks.add_task(_run_refresh_task)
    return {
        "success": True,
        "message": "Stories refresh started in background",
        "is_background": True,
        "refreshing": True
    }

@router.get("/sources")
async def get_available_sources():
    """Get list of available news sources with status"""
    try:
        sources = crawler_service.get_available_sources()
        active_sources = crawler_service.get_active_sources()

        # Add status to each source
        for source in sources:
            source['is_active'] = source['domain'] in active_sources
            source['is_custom'] = source.get('is_custom', source_config.is_custom(source['domain']))
            
        return {
            "success": True,
            "sources": sources,
            "count": len(sources),
            "active_count": len(active_sources),
            "total_count": len(sources),
            "active_sources": active_sources
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/sources/{domain}/status")
async def update_source_status(domain: str, update: SourceStatusUpdate):
    """Activate or deactivate a news source"""
    normalized = domain.strip().lower()
    try:
        from services.sources import NEWS_SOURCES  # Local import to avoid circular dependency

        if normalized not in NEWS_SOURCES and not source_config.is_custom(normalized):
            raise HTTPException(status_code=404, detail="Source not found")

        source_config.set_source_active(normalized, update.active)
        return {
            "success": True,
            "domain": normalized,
            "is_active": update.active,
            "sources": crawler_service.get_available_sources()
        }
    except HTTPException:
        raise
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))
    except Exception as exc:  # pragma: no cover - defensive
        raise HTTPException(status_code=500, detail=str(exc))


@router.post("/sources")
async def add_source(request: SourceCreateRequest):
    """Add a new custom news source"""
    try:
        created = source_config.add_custom_source(
            domain=request.domain,
            name=request.name,
            rss_urls=request.rss_urls,
            fallback_urls=request.fallback_urls,
            activate=request.activate
        )

        from services.sources import NEWS_SOURCES, NewsSource

        NEWS_SOURCES[created['domain']] = NewsSource(
            domain=created['domain'],
            name=created['name'],
            rss_urls=created.get('rss_urls', []),
            fallback_urls=created.get('fallback_urls', [])
        )

        return {
            "success": True,
            "source": {
                "domain": created['domain'],
                "name": created['name'],
                "rss_urls": created.get('rss_urls', []),
                "fallback_urls": created.get('fallback_urls', []),
                "is_custom": True,
                "is_active": request.activate,
                "has_rss": bool(created.get('rss_urls'))
            },
            "sources": crawler_service.get_available_sources()
        }
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))
    except Exception as exc:  # pragma: no cover
        raise HTTPException(status_code=500, detail=str(exc))


@router.post("/stories/delete")
async def delete_stories(request: StoriesDeleteRequest):
    """Delete selected stories or clear all stories when none provided."""
    try:
        story_ids = request.story_ids or None
        deleted = crawler_service.delete_stories(story_ids)
        return {
            "success": True,
            "deleted": deleted
        }
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))

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
