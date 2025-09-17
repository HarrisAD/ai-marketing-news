import logging
from typing import List, Dict, Set, Tuple
from simhash import Simhash
import re
from urllib.parse import urlparse

logger = logging.getLogger(__name__)

class DeduplicationService:
    """Service for detecting and handling duplicate stories"""
    
    def __init__(self, similarity_threshold: int = 3):
        """
        Initialize deduplication service
        
        Args:
            similarity_threshold: Max hamming distance for simhash (lower = more similar)
        """
        self.similarity_threshold = similarity_threshold
        
    def deduplicate_stories(self, stories: List[Dict]) -> List[Dict]:
        """
        Deduplicate a list of stories, marking duplicates and selecting canonical versions
        
        Returns:
            List of stories with deduplication metadata added
        """
        if len(stories) <= 1:
            return stories
        
        logger.info(f"Deduplicating {len(stories)} stories")
        
        # Group stories by similarity
        similarity_groups = self._group_similar_stories(stories)
        
        # Process each group to select canonical story and mark duplicates
        deduplicated_stories = []
        
        for group in similarity_groups:
            if len(group) == 1:
                # Single story, mark as canonical
                story = group[0]
                story['is_canonical'] = True
                story['similar_stories'] = []
                deduplicated_stories.append(story)
            else:
                # Multiple similar stories, select canonical and mark others
                canonical_story, duplicate_stories = self._select_canonical_story(group)
                
                # Mark canonical story
                canonical_story['is_canonical'] = True
                canonical_story['similar_stories'] = [s['id'] for s in duplicate_stories]
                deduplicated_stories.append(canonical_story)
                
                # Mark duplicate stories
                for duplicate in duplicate_stories:
                    duplicate['is_canonical'] = False
                    duplicate['similar_stories'] = [canonical_story['id']]
                    deduplicated_stories.append(duplicate)
        
        canonical_count = len([s for s in deduplicated_stories if s.get('is_canonical', True)])
        logger.info(f"Deduplication result: {canonical_count} canonical stories from {len(stories)} total")
        
        return deduplicated_stories
    
    def _group_similar_stories(self, stories: List[Dict]) -> List[List[Dict]]:
        """Group stories by content similarity using simhash"""
        
        # Calculate simhash for each story
        story_hashes = []
        for story in stories:
            content_text = self._extract_content_for_hashing(story)
            try:
                simhash_value = Simhash(content_text)
            except Exception as exc:  # pragma: no cover - defensive fallback
                logger.warning(f"Simhash calculation failed for story '{story.get('title', 'Unknown')}': {exc}")
                simhash_value = None
            story_hashes.append((story, simhash_value))
        
        # Group similar stories
        groups = []
        used_indices = set()
        
        for i, (story1, hash1) in enumerate(story_hashes):
            if i in used_indices:
                continue
            
            # Start new group with current story
            group = [story1]
            used_indices.add(i)
            
            # Find similar stories
            for j, (story2, hash2) in enumerate(story_hashes):
                if j in used_indices:
                    continue
                
                # Check if stories are similar
                if self._are_stories_similar(story1, story2, hash1, hash2):
                    group.append(story2)
                    used_indices.add(j)
            
            groups.append(group)
        
        return groups
    
    def _are_stories_similar(self, story1: Dict, story2: Dict, 
                           hash1: Simhash, hash2: Simhash) -> bool:
        """Determine if two stories are similar enough to be considered duplicates"""
        
        # If either hash missing, skip simhash comparison
        if hash1 is None or hash2 is None:
            return False
        # First check: content similarity using simhash
        hamming_distance = hash1.distance(hash2)
        if hamming_distance > self.similarity_threshold:
            return False
        
        # Second check: URL similarity (same domain or very similar paths)
        url1 = story1.get('canonical_url', '')
        url2 = story2.get('canonical_url', '')
        
        if url1 == url2:
            return True
        
        # Parse URLs
        parsed1 = urlparse(url1)
        parsed2 = urlparse(url2)
        
        # Different domains - less likely to be duplicates unless content is very similar
        if parsed1.netloc != parsed2.netloc:
            return hamming_distance <= 1  # Very strict for cross-domain
        
        # Same domain - check path similarity
        path1 = parsed1.path.lower()
        path2 = parsed2.path.lower()
        
        # Remove common path elements for comparison
        clean_path1 = self._clean_url_path(path1)
        clean_path2 = self._clean_url_path(path2)
        
        if clean_path1 == clean_path2:
            return True
        
        # Third check: title similarity
        title1 = story1.get('title', '').lower()
        title2 = story2.get('title', '').lower()
        
        # Simple title similarity check
        title_similarity = self._calculate_title_similarity(title1, title2)
        if title_similarity > 0.8:  # 80% similar titles
            return True
        
        return False
    
    def _select_canonical_story(self, similar_stories: List[Dict]) -> Tuple[Dict, List[Dict]]:
        """
        Select the best story as canonical from a group of similar stories
        
        Selection criteria (in order of priority):
        1. Highest marketing relevance score
        2. Most complete content
        3. Most authoritative source
        4. Most recent publication date
        """
        
        if len(similar_stories) == 1:
            return similar_stories[0], []
        
        # Sort by selection criteria
        def story_score(story):
            # Primary: marketing score
            marketing_score = story.get('score', 0)
            
            # Secondary: content completeness
            content_length = len(story.get('content', ''))
            
            # Tertiary: source authority (prefer major sources)
            source_domain = story.get('source_domain', '')
            authority_bonus = 0
            if any(domain in source_domain for domain in ['openai.com', 'anthropic.com', 'microsoft.com', 'google.com']):
                authority_bonus = 10
            
            # Quaternary: recency (more recent is better)
            published_date = story.get('published_date')
            recency_bonus = 0
            if published_date:
                # Convert to timestamp for comparison
                if hasattr(published_date, 'timestamp'):
                    recency_bonus = published_date.timestamp() / 1000000  # Small contribution
            
            return (marketing_score + authority_bonus, content_length, recency_bonus)
        
        # Sort stories by criteria (highest first)
        sorted_stories = sorted(similar_stories, key=story_score, reverse=True)
        
        canonical = sorted_stories[0]
        duplicates = sorted_stories[1:]
        
        logger.debug(f"Selected canonical story: '{canonical.get('title', '')}' from {len(similar_stories)} similar stories")
        
        return canonical, duplicates
    
    def _extract_content_for_hashing(self, story: Dict) -> str:
        """Extract and normalize content for similarity hashing"""
        
        # Combine title and content
        title = story.get('title', '')
        content = story.get('content', '')
        description = story.get('description', '')
        
        # Use content, fallback to description, then title
        text = content or description or title
        
        # Normalize text for better comparison
        text = self._normalize_text(text)
        
        return text
    
    def _normalize_text(self, text: str) -> str:
        """Normalize text for better similarity detection"""
        
        # Convert to lowercase
        text = text.lower()
        
        # Remove extra whitespace
        text = re.sub(r'\s+', ' ', text)
        
        # Remove punctuation except spaces
        text = re.sub(r'[^\w\s]', '', text)
        
        # Remove common stop words that don't affect meaning
        stop_words = {
            'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 
            'of', 'with', 'by', 'this', 'that', 'these', 'those', 'is', 'are', 
            'was', 'were', 'be', 'been', 'being', 'have', 'has', 'had', 'do', 
            'does', 'did', 'will', 'would', 'could', 'should', 'may', 'might'
        }
        
        words = text.split()
        words = [word for word in words if word not in stop_words and len(word) > 2]
        
        return ' '.join(words)
    
    def _clean_url_path(self, path: str) -> str:
        """Clean URL path for similarity comparison"""
        
        # Remove file extensions
        path = re.sub(r'\.[a-zA-Z0-9]+$', '', path)
        
        # Remove common path elements
        path = re.sub(r'/(news|blog|article|post|story)/', '/', path)
        
        # Remove trailing slashes
        path = path.rstrip('/')
        
        # Remove date patterns
        path = re.sub(r'/\d{4}/\d{2}/\d{2}/', '/', path)
        path = re.sub(r'/\d{4}/\d{2}/', '/', path)
        path = re.sub(r'/\d{4}/', '/', path)
        
        return path
    
    def _calculate_title_similarity(self, title1: str, title2: str) -> float:
        """Calculate simple similarity between two titles"""
        
        if not title1 or not title2:
            return 0.0
        
        # Normalize titles
        title1 = self._normalize_text(title1)
        title2 = self._normalize_text(title2)
        
        words1 = set(title1.split())
        words2 = set(title2.split())
        
        if not words1 or not words2:
            return 0.0
        
        # Jaccard similarity
        intersection = len(words1.intersection(words2))
        union = len(words1.union(words2))
        
        return intersection / union if union > 0 else 0.0
