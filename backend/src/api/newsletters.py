from fastapi import APIRouter, HTTPException
from fastapi.responses import PlainTextResponse
from typing import List, Optional
from datetime import datetime
from pydantic import BaseModel, Field
from models.story import NewsletterRequest, NewsletterResponse
from services.crawler_service import CrawlerService

router = APIRouter(prefix="/api", tags=["newsletters"])
crawler_service = CrawlerService()

class NewsletterGenerateRequest(BaseModel):
    date_from: datetime = Field(..., description="Start date for story selection")
    date_to: datetime = Field(..., description="End date for story selection")
    min_score: int = Field(default=60, ge=0, le=100, description="Minimum story score")
    selected_story_ids: List[str] = Field(default_factory=list, description="Specific story IDs to include")
    editorial_instructions: str = Field(default="", description="Editorial tone/theme instructions")
    max_stories: int = Field(default=10, ge=1, le=50, description="Maximum number of stories")

@router.post("/newsletters/render")
async def generate_newsletter(request: NewsletterGenerateRequest):
    """Generate a newsletter from selected stories or date range"""
    try:
        result = crawler_service.generate_newsletter(
            date_from=request.date_from,
            date_to=request.date_to,
            min_score=request.min_score,
            selected_story_ids=request.selected_story_ids,
            editorial_instructions=request.editorial_instructions,
            max_stories=request.max_stories
        )
        
        if result['success']:
            return {
                "success": True,
                "newsletter": {
                    "newsletter_id": result['newsletter_id'],
                    "content": result['content'],
                    "story_count": result['story_count'],
                    "stories_used": result['stories_used'],
                    "generated_date": datetime.now().isoformat()
                }
            }
        else:
            raise HTTPException(status_code=400, detail=result.get('error', 'Newsletter generation failed'))
            
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/newsletters")
async def list_newsletters():
    """List all generated newsletters"""
    try:
        newsletters = crawler_service.list_newsletters()
        return {
            "success": True,
            "newsletters": newsletters,
            "count": len(newsletters)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/newsletters/{newsletter_id}")
async def get_newsletter(newsletter_id: str):
    """Get newsletter content and metadata"""
    try:
        result = crawler_service.get_newsletter(newsletter_id)
        
        if result['success']:
            return {
                "success": True,
                "newsletter": {
                    "newsletter_id": newsletter_id,
                    "content": result['content'],
                    "metadata": result['metadata']
                }
            }
        else:
            raise HTTPException(status_code=404, detail="Newsletter not found")
            
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/newsletters/{newsletter_id}/markdown", response_class=PlainTextResponse)
async def download_newsletter_markdown(newsletter_id: str):
    """Download newsletter as Markdown file"""
    try:
        result = crawler_service.get_newsletter(newsletter_id)
        
        if result['success']:
            return PlainTextResponse(
                content=result['content'],
                media_type="text/markdown",
                headers={"Content-Disposition": f"attachment; filename={newsletter_id}.md"}
            )
        else:
            raise HTTPException(status_code=404, detail="Newsletter not found")
            
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/newsletters/{newsletter_id}/stories")
async def get_newsletter_stories(newsletter_id: str):
    """Get the stories used in a specific newsletter"""
    try:
        result = crawler_service.get_newsletter(newsletter_id)
        
        if not result['success']:
            raise HTTPException(status_code=404, detail="Newsletter not found")
        
        story_ids = result['metadata'].get('stories_used', [])
        stories = []
        
        for story_id in story_ids:
            story = crawler_service.get_story_by_id(story_id)
            if story:
                stories.append(story)
        
        return {
            "success": True,
            "newsletter_id": newsletter_id,
            "stories": stories,
            "count": len(stories)
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Analytics endpoint for newsletter performance
@router.get("/newsletters/{newsletter_id}/analytics")
async def get_newsletter_analytics(newsletter_id: str):
    """Get analytics for a specific newsletter"""
    try:
        result = crawler_service.get_newsletter(newsletter_id)
        
        if not result['success']:
            raise HTTPException(status_code=404, detail="Newsletter not found")
        
        metadata = result['metadata']
        story_ids = metadata.get('stories_used', [])
        
        # Get story details for analytics
        stories = []
        for story_id in story_ids:
            story = crawler_service.get_story_by_id(story_id)
            if story:
                stories.append(story)
        
        # Calculate analytics
        if stories:
            scores = [s.get('score', 0) for s in stories]
            avg_score = sum(scores) / len(scores)
            max_score = max(scores)
            min_score = min(scores)
            
            # Source distribution
            sources = {}
            for story in stories:
                source = story.get('source_name', 'Unknown')
                sources[source] = sources.get(source, 0) + 1
            
            # Tag distribution
            tags = {}
            for story in stories:
                for tag in story.get('tags', []):
                    tags[tag] = tags.get(tag, 0) + 1
        else:
            avg_score = max_score = min_score = 0
            sources = {}
            tags = {}
        
        return {
            "success": True,
            "newsletter_id": newsletter_id,
            "analytics": {
                "story_count": len(stories),
                "score_stats": {
                    "average": round(avg_score, 1),
                    "maximum": max_score,
                    "minimum": min_score
                },
                "source_distribution": sources,
                "tag_distribution": tags,
                "generated_date": metadata.get('generated_date'),
                "date_range": {
                    "from": metadata.get('date_from'),
                    "to": metadata.get('date_to')
                }
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))