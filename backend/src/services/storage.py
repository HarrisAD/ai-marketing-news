import json
import os
import logging
from typing import List, Dict, Optional, Iterator
from datetime import datetime, timedelta
import portalocker
from pathlib import Path
from models.story import Story
from services.config import settings

logger = logging.getLogger(__name__)

class TextStore:
    """JSONL-based storage system for stories"""
    
    def __init__(self, data_dir: str = None):
        self.data_dir = Path(data_dir or settings.data_dir)
        self.data_dir.mkdir(exist_ok=True)
        self.stories_file = self.data_dir / "stories.jsonl"
        self.newsletters_dir = self.data_dir / "newsletters"
        self.newsletters_dir.mkdir(exist_ok=True)
        
        # Ensure stories file exists
        if not self.stories_file.exists():
            self.stories_file.touch()
    
    def save_stories(self, stories: List[Dict]) -> int:
        """Save multiple stories to storage, avoiding duplicates"""
        if not stories:
            return 0
        
        existing_ids = set(self.get_all_story_ids())
        new_stories = [s for s in stories if s['id'] not in existing_ids]
        
        if not new_stories:
            logger.info("No new stories to save")
            return 0
        
        try:
            with open(self.stories_file, 'a', encoding='utf-8') as f:
                portalocker.lock(f, portalocker.LOCK_EX)
                
                for story in new_stories:
                    # Ensure datetime objects are properly serialized
                    story_copy = self._serialize_story(story)
                    f.write(json.dumps(story_copy, ensure_ascii=False) + '\n')
                
                portalocker.unlock(f)
            
            logger.info(f"Saved {len(new_stories)} new stories")
            return len(new_stories)
            
        except Exception as e:
            logger.error(f"Failed to save stories: {e}")
            return 0
    
    def get_all_stories(self, min_score: int = None, source_domain: str = None, 
                       days_back: int = None) -> List[Dict]:
        """Retrieve all stories with optional filtering"""
        stories = []
        
        try:
            if not self.stories_file.exists():
                return stories
            
            with open(self.stories_file, 'r', encoding='utf-8') as f:
                portalocker.lock(f, portalocker.LOCK_SH)
                
                for line in f:
                    line = line.strip()
                    if not line:
                        continue
                    
                    try:
                        story = json.loads(line)
                        story = self._deserialize_story(story)
                        
                        # Apply filters
                        if min_score is not None and story.get('score', 0) < min_score:
                            continue
                        
                        if source_domain and story.get('source_domain') != source_domain:
                            continue
                        
                        if days_back:
                            story_date = datetime.fromisoformat(story['published_date'].replace('Z', '+00:00'))
                            cutoff = datetime.now().replace(tzinfo=story_date.tzinfo) - timedelta(days=int(days_back))
                            if story_date < cutoff:
                                continue
                        
                        stories.append(story)
                        
                    except json.JSONDecodeError as e:
                        logger.warning(f"Failed to parse story line: {e}")
                        continue
                
                portalocker.unlock(f)
            
        except Exception as e:
            logger.error(f"Failed to load stories: {e}")
        
        return stories
    
    def get_story_by_id(self, story_id: str) -> Optional[Dict]:
        """Retrieve a specific story by ID"""
        try:
            with open(self.stories_file, 'r', encoding='utf-8') as f:
                portalocker.lock(f, portalocker.LOCK_SH)
                
                for line in f:
                    line = line.strip()
                    if not line:
                        continue
                    
                    try:
                        story = json.loads(line)
                        if story.get('id') == story_id:
                            portalocker.unlock(f)
                            return self._deserialize_story(story)
                    except json.JSONDecodeError:
                        continue
                
                portalocker.unlock(f)
        
        except Exception as e:
            logger.error(f"Failed to get story {story_id}: {e}")
        
        return None
    
    def get_all_story_ids(self) -> List[str]:
        """Get all story IDs (for duplicate checking)"""
        ids = []
        
        try:
            if not self.stories_file.exists():
                return ids
            
            with open(self.stories_file, 'r', encoding='utf-8') as f:
                portalocker.lock(f, portalocker.LOCK_SH)
                
                for line in f:
                    line = line.strip()
                    if not line:
                        continue
                    
                    try:
                        story = json.loads(line)
                        ids.append(story.get('id'))
                    except json.JSONDecodeError:
                        continue
                
                portalocker.unlock(f)
        
        except Exception as e:
            logger.error(f"Failed to load story IDs: {e}")
        
        return ids
    
    def update_story(self, story_id: str, updates: Dict) -> bool:
        """Update a specific story (useful for deduplication)"""
        # For simplicity, we'll reload all stories, update the target, and rewrite
        # In production, you might want a more efficient approach
        
        try:
            all_stories = self.get_all_stories()
            updated = False
            
            for story in all_stories:
                if story['id'] == story_id:
                    story.update(updates)
                    updated = True
                    break
            
            if updated:
                # Rewrite the entire file
                self._rewrite_stories_file(all_stories)
                logger.info(f"Updated story {story_id}")
                return True
            
        except Exception as e:
            logger.error(f"Failed to update story {story_id}: {e}")
        
        return False
    
    def save_newsletter(self, newsletter_id: str, content: str, 
                       stories_used: List[str], metadata: Dict = None) -> bool:
        """Save newsletter content and metadata"""
        try:
            # Save markdown content
            md_file = self.newsletters_dir / f"{newsletter_id}.md"
            with open(md_file, 'w', encoding='utf-8') as f:
                f.write(content)
            
            # Save metadata with story references
            meta_data = {
                'newsletter_id': newsletter_id,
                'generated_date': datetime.now().isoformat(),
                'stories_used': stories_used,
                'story_count': len(stories_used),
                'metadata': metadata or {}
            }
            
            json_file = self.newsletters_dir / f"{newsletter_id}.json"
            with open(json_file, 'w', encoding='utf-8') as f:
                json.dump(meta_data, f, indent=2, ensure_ascii=False)
            
            logger.info(f"Saved newsletter {newsletter_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to save newsletter {newsletter_id}: {e}")
            return False
    
    def get_newsletter_content(self, newsletter_id: str) -> Optional[str]:
        """Get newsletter markdown content"""
        try:
            md_file = self.newsletters_dir / f"{newsletter_id}.md"
            if md_file.exists():
                return md_file.read_text(encoding='utf-8')
        except Exception as e:
            logger.error(f"Failed to load newsletter {newsletter_id}: {e}")
        return None
    
    def get_newsletter_metadata(self, newsletter_id: str) -> Optional[Dict]:
        """Get newsletter metadata"""
        try:
            json_file = self.newsletters_dir / f"{newsletter_id}.json"
            if json_file.exists():
                with open(json_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
        except Exception as e:
            logger.error(f"Failed to load newsletter metadata {newsletter_id}: {e}")
        return None
    
    def list_newsletters(self) -> List[Dict]:
        """List all newsletters with metadata"""
        newsletters = []
        
        try:
            for json_file in self.newsletters_dir.glob("*.json"):
                try:
                    with open(json_file, 'r', encoding='utf-8') as f:
                        metadata = json.load(f)
                        newsletters.append(metadata)
                except Exception as e:
                    logger.warning(f"Failed to load newsletter metadata {json_file}: {e}")
        except Exception as e:
            logger.error(f"Failed to list newsletters: {e}")
        
        # Sort by generated date (newest first)
        newsletters.sort(key=lambda x: x.get('generated_date', ''), reverse=True)
        return newsletters
    
    def get_stats(self) -> Dict:
        """Get storage statistics"""
        try:
            all_stories = self.get_all_stories()
            newsletters = self.list_newsletters()
            
            # Calculate score distribution
            scores = [s.get('score', 0) for s in all_stories if s.get('score') is not None]
            score_ranges = {
                '90-100': len([s for s in scores if s >= 90]),
                '80-89': len([s for s in scores if 80 <= s < 90]),
                '70-79': len([s for s in scores if 70 <= s < 80]),
                '60-69': len([s for s in scores if 60 <= s < 70]),
                '0-59': len([s for s in scores if s < 60])
            }
            
            # Source distribution
            sources = {}
            for story in all_stories:
                domain = story.get('source_domain', 'unknown')
                sources[domain] = sources.get(domain, 0) + 1
            
            return {
                'total_stories': len(all_stories),
                'total_newsletters': len(newsletters),
                'score_distribution': score_ranges,
                'source_distribution': sources,
                'average_score': sum(scores) / len(scores) if scores else 0,
                'data_dir': str(self.data_dir),
                'stories_file_size': self.stories_file.stat().st_size if self.stories_file.exists() else 0
            }
            
        except Exception as e:
            logger.error(f"Failed to get stats: {e}")
            return {}
    
    def _serialize_story(self, story: Dict) -> Dict:
        """Convert datetime objects to ISO strings for JSON storage"""
        story_copy = story.copy()
        
        for key in ['published_date', 'fetched_date']:
            if key in story_copy and isinstance(story_copy[key], datetime):
                story_copy[key] = story_copy[key].isoformat()
        
        return story_copy
    
    def _deserialize_story(self, story: Dict) -> Dict:
        """Convert ISO strings back to datetime objects"""
        story_copy = story.copy()
        
        for key in ['published_date', 'fetched_date']:
            if key in story_copy and isinstance(story_copy[key], str):
                try:
                    story_copy[key] = datetime.fromisoformat(story_copy[key].replace('Z', '+00:00'))
                except ValueError:
                    # Keep as string if parsing fails
                    pass
        
        return story_copy
    
    def _rewrite_stories_file(self, stories: List[Dict]):
        """Rewrite the entire stories file (for updates)"""
        backup_file = self.stories_file.with_suffix('.backup')
        
        try:
            # Create backup
            if self.stories_file.exists():
                backup_file.write_bytes(self.stories_file.read_bytes())
            
            # Write new content
            with open(self.stories_file, 'w', encoding='utf-8') as f:
                portalocker.lock(f, portalocker.LOCK_EX)
                
                for story in stories:
                    story_copy = self._serialize_story(story)
                    f.write(json.dumps(story_copy, ensure_ascii=False) + '\n')
                
                portalocker.unlock(f)
            
            # Remove backup if successful
            if backup_file.exists():
                backup_file.unlink()
                
        except Exception as e:
            # Restore from backup if write failed
            if backup_file.exists():
                self.stories_file.write_bytes(backup_file.read_bytes())
                backup_file.unlink()
            raise e