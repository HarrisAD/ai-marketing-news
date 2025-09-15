import logging
from typing import List, Dict
from datetime import datetime
from services.sources import NewsCrawler
from services.llm_service import LLMService
from services.storage import TextStore
from services.deduplication import DeduplicationService
from services.config import settings

logger = logging.getLogger(__name__)

class CrawlerService:
    """Main service that orchestrates the news crawling, scoring, and storage process"""
    
    def __init__(self):
        self.news_crawler = NewsCrawler(
            days_back=settings.crawler_days_back,
            max_stories_per_source=settings.max_stories_per_source
        )
        self.llm_service = LLMService()
        self.storage = TextStore()
        self.deduplication_service = DeduplicationService()
    
    def run_full_update(self, source_domains: List[str] = None) -> Dict:
        """
        Run the complete news update process:
        1. Crawl news sources
        2. Score stories with LLM
        3. Deduplicate stories
        4. Save to storage
        """
        
        start_time = datetime.now()
        logger.info("🚀 Starting full news update process...")
        
        # Use configured sources if none specified
        if source_domains is None:
            source_domains = settings.source_list
        
        try:
            # Step 1: Crawl news sources
            logger.info(f"📰 Crawling {len(source_domains)} news sources...")
            raw_stories = self.news_crawler.crawl_sources(source_domains)
            
            if not raw_stories:
                logger.warning("No stories found from any source")
                return {
                    'success': True,
                    'stories_crawled': 0,
                    'stories_scored': 0,
                    'stories_saved': 0,
                    'duration_seconds': 0,
                    'message': 'No new stories found'
                }
            
            logger.info(f"✅ Crawled {len(raw_stories)} raw stories")
            
            # Step 2: Score stories with LLM
            logger.info("🤖 Scoring stories with LLM...")
            scored_stories = []
            
            for i, story in enumerate(raw_stories, 1):
                try:
                    logger.info(f"Scoring story {i}/{len(raw_stories)}: {story.get('title', 'Unknown')[:50]}...")
                    scored_story = self.llm_service.score_story(story)
                    scored_stories.append(scored_story)
                except Exception as e:
                    logger.error(f"Failed to score story {i}: {e}")
                    # Add story with default scores
                    story.update({
                        'score': 0,
                        'marketer_relevance': [],
                        'action_hint': '',
                        'tags': []
                    })
                    scored_stories.append(story)
            
            logger.info(f"✅ Scored {len(scored_stories)} stories")
            
            # Step 3: Deduplicate stories
            logger.info("🔍 Deduplicating stories...")
            deduplicated_stories = self.deduplication_service.deduplicate_stories(scored_stories)
            logger.info(f"✅ Deduplication complete")
            
            # Step 4: Save to storage
            logger.info("💾 Saving stories to storage...")
            saved_count = self.storage.save_stories(deduplicated_stories)
            
            end_time = datetime.now()
            duration = (end_time - start_time).total_seconds()
            
            result = {
                'success': True,
                'stories_crawled': len(raw_stories),
                'stories_scored': len(scored_stories),
                'stories_saved': saved_count,
                'duration_seconds': duration,
                'sources_processed': source_domains,
                'timestamp': end_time.isoformat()
            }
            
            logger.info(f"🎉 Update complete! Saved {saved_count} new stories in {duration:.1f}s")
            return result
            
        except Exception as e:
            end_time = datetime.now()
            duration = (end_time - start_time).total_seconds()
            
            logger.error(f"❌ Update failed after {duration:.1f}s: {e}")
            return {
                'success': False,
                'error': str(e),
                'duration_seconds': duration,
                'timestamp': end_time.isoformat()
            }
    
    def get_stories(self, min_score: int = None, source_domain: str = None, 
                   days_back: int = None, limit: int = None) -> List[Dict]:
        """Get stories with filtering options"""
        
        stories = self.storage.get_all_stories(
            min_score=min_score,
            source_domain=source_domain,
            days_back=days_back
        )
        
        # Sort by score (highest first), then by date (newest first)
        stories.sort(key=lambda x: (
            x.get('score', 0),
            x.get('published_date', datetime.min)
        ), reverse=True)
        
        if limit:
            stories = stories[:limit]
        
        return stories
    
    def get_story_by_id(self, story_id: str) -> Dict:
        """Get a specific story by ID"""
        return self.storage.get_story_by_id(story_id)
    
    def generate_newsletter(self, date_from: datetime, date_to: datetime,
                          min_score: int = 60, selected_story_ids: List[str] = None,
                          editorial_instructions: str = "", max_stories: int = 10) -> Dict:
        """Generate a newsletter from selected or filtered stories"""
        
        try:
            # Get stories in date range
            all_stories = self.storage.get_all_stories()
            
            # Filter by date range
            filtered_stories = []
            for story in all_stories:
                story_date = story.get('published_date')
                if isinstance(story_date, str):
                    try:
                        story_date = datetime.fromisoformat(story_date.replace('Z', '+00:00'))
                    except ValueError:
                        continue
                
                if date_from <= story_date <= date_to:
                    filtered_stories.append(story)
            
            # Use selected stories if provided, otherwise filter by score
            if selected_story_ids:
                newsletter_stories = [s for s in filtered_stories if s['id'] in selected_story_ids]
            else:
                # Auto-select high-scoring stories
                newsletter_stories = [s for s in filtered_stories if s.get('score', 0) >= min_score]
                newsletter_stories.sort(key=lambda x: x.get('score', 0), reverse=True)
                newsletter_stories = newsletter_stories[:max_stories]
            
            if not newsletter_stories:
                return {
                    'success': False,
                    'error': 'No stories found matching criteria'
                }
            
            # Generate newsletter content
            logger.info(f"Generating newsletter with {len(newsletter_stories)} stories")
            newsletter_content = self.llm_service.generate_newsletter(
                newsletter_stories, 
                editorial_instructions
            )
            
            # Save newsletter
            newsletter_id = date_from.strftime('%Y-%m-%d')
            story_ids = [s['id'] for s in newsletter_stories]
            
            success = self.storage.save_newsletter(
                newsletter_id=newsletter_id,
                content=newsletter_content,
                stories_used=story_ids,
                metadata={
                    'date_from': date_from.isoformat(),
                    'date_to': date_to.isoformat(),
                    'min_score': min_score,
                    'editorial_instructions': editorial_instructions
                }
            )
            
            if success:
                return {
                    'success': True,
                    'newsletter_id': newsletter_id,
                    'content': newsletter_content,
                    'stories_used': story_ids,
                    'story_count': len(newsletter_stories)
                }
            else:
                return {
                    'success': False,
                    'error': 'Failed to save newsletter'
                }
                
        except Exception as e:
            logger.error(f"Failed to generate newsletter: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def get_newsletter(self, newsletter_id: str) -> Dict:
        """Get newsletter content and metadata"""
        
        content = self.storage.get_newsletter_content(newsletter_id)
        metadata = self.storage.get_newsletter_metadata(newsletter_id)
        
        if content and metadata:
            return {
                'success': True,
                'newsletter_id': newsletter_id,
                'content': content,
                'metadata': metadata
            }
        else:
            return {
                'success': False,
                'error': 'Newsletter not found'
            }
    
    def list_newsletters(self) -> List[Dict]:
        """List all newsletters"""
        return self.storage.list_newsletters()
    
    def get_stats(self) -> Dict:
        """Get system statistics"""
        return self.storage.get_stats()
    
    def get_available_sources(self) -> List[Dict]:
        """Get list of available news sources"""
        from services.sources import NEWS_SOURCES
        
        sources = []
        for domain, source in NEWS_SOURCES.items():
            sources.append({
                'domain': domain,
                'name': source.name,
                'rss_urls': source.rss_urls,
                'fallback_urls': source.fallback_urls
            })
        
        return sources
    
    def get_available_tags(self) -> List[str]:
        """Get list of available story tags"""
        from models.story import StoryTag
        return [tag.value for tag in StoryTag]