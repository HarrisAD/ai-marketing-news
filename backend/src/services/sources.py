from datetime import datetime, timedelta
from typing import List, Dict, Optional
import feedparser
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
import hashlib
import logging

from services.source_config import source_config

logger = logging.getLogger(__name__)

class NewsSource:
    def __init__(self, domain: str, name: str, rss_urls: List[str], fallback_urls: List[str] = None):
        self.domain = domain
        self.name = name
        self.rss_urls = rss_urls
        self.fallback_urls = fallback_urls or []

# News source definitions
NEWS_SOURCES = {
    "openai.com": NewsSource(
        domain="openai.com",
        name="OpenAI",
        rss_urls=["https://openai.com/news/rss.xml"],
        fallback_urls=["https://openai.com/news"]
    ),
    "anthropic.com": NewsSource(
        domain="anthropic.com", 
        name="Anthropic",
        rss_urls=[],
        fallback_urls=["https://www.anthropic.com/news"]
    ),
    "microsoft.com": NewsSource(
        domain="microsoft.com",
        name="Microsoft AI",
        rss_urls=["https://blogs.microsoft.com/ai/feed/"],
        fallback_urls=["https://blogs.microsoft.com/ai/"]
    ),
    "google.com": NewsSource(
        domain="google.com",
        name="Google AI",
        rss_urls=["https://blog.google/technology/ai/rss/"],
        fallback_urls=["https://blog.google/technology/ai/"]
    ),
    "meta.com": NewsSource(
        domain="meta.com",
        name="Meta AI",
        rss_urls=["https://ai.meta.com/blog/rss/"],
        fallback_urls=["https://ai.meta.com/blog/"]
    ),
    "perplexity.ai": NewsSource(
        domain="perplexity.ai",
        name="Perplexity",
        rss_urls=[],
        fallback_urls=["https://blog.perplexity.ai/"]
    ),
    "oneusefulthing.org": NewsSource(
        domain="oneusefulthing.org",
        name="One Useful Thing",
        rss_urls=["https://www.oneusefulthing.org/feed"],
        fallback_urls=["https://www.oneusefulthing.org/"]
    ),
    "marketingaiinstitute.com": NewsSource(
        domain="marketingaiinstitute.com",
        name="Marketing AI Institute",
        rss_urls=["https://www.marketingaiinstitute.com/feed"],
        fallback_urls=["https://www.marketingaiinstitute.com/blog"]
    ),
    "economist.com": NewsSource(
        domain="economist.com",
        name="The Economist",
        rss_urls=["https://www.economist.com/technology/rss.xml"],
        fallback_urls=["https://www.economist.com/technology"]
    ),
    "forbes.com": NewsSource(
        domain="forbes.com",
        name="Forbes",
        rss_urls=["https://www.forbes.com/ai-big-data/feed/"],
        fallback_urls=["https://www.forbes.com/ai-big-data/"]
    ),
    "fortune.com": NewsSource(
        domain="fortune.com",
        name="Fortune",
        rss_urls=["https://fortune.com/section/artificial-intelligence/feed/"],
        fallback_urls=["https://fortune.com/section/artificial-intelligence/"]
    ),
    "technologyreview.com": NewsSource(
        domain="technologyreview.com",
        name="MIT Technology Review",
        rss_urls=["https://www.technologyreview.com/topicai/feed/"],
        fallback_urls=["https://www.technologyreview.com/topic/artificial-intelligence/"]
    ),
    "techcrunch.com": NewsSource(
        domain="techcrunch.com",
        name="TechCrunch AI",
        rss_urls=["https://techcrunch.com/category/artificial-intelligence/feed/"],
        fallback_urls=["https://techcrunch.com/category/artificial-intelligence/"]
    ),
    "venturebeat.com": NewsSource(
        domain="venturebeat.com", 
        name="VentureBeat AI",
        rss_urls=["https://venturebeat.com/ai/feed/"],
        fallback_urls=["https://venturebeat.com/ai/"]
    ),
    "theverge.com": NewsSource(
        domain="theverge.com",
        name="The Verge AI",
        rss_urls=["https://www.theverge.com/ai-artificial-intelligence/rss/index.xml"],
        fallback_urls=["https://www.theverge.com/ai-artificial-intelligence"]
    ),
    "wired.com": NewsSource(
        domain="wired.com",
        name="Wired AI",
        rss_urls=["https://www.wired.com/feed/tag/ai/latest/rss"],
        fallback_urls=["https://www.wired.com/tag/artificial-intelligence/"]
    ),
    "hubspot.com": NewsSource(
        domain="hubspot.com",
        name="HubSpot AI",
        rss_urls=["https://blog.hubspot.com/marketing/topic/artificial-intelligence/rss.xml"],
        fallback_urls=["https://blog.hubspot.com/marketing/topic/artificial-intelligence"]
    ),
    "salesforce.com": NewsSource(
        domain="salesforce.com",
        name="Salesforce AI",
        rss_urls=["https://www.salesforce.com/news/rss/"],
        fallback_urls=["https://www.salesforce.com/news/", "https://www.salesforce.com/products/einstein/"]
    ),
    "adobe.com": NewsSource(
        domain="adobe.com",
        name="Adobe AI",
        rss_urls=[],
        fallback_urls=["https://blog.adobe.com/en/topics/artificial-intelligence"]
    ),
    "nvidia.com": NewsSource(
        domain="nvidia.com", 
        name="NVIDIA AI",
        rss_urls=["https://blogs.nvidia.com/feed/"],
        fallback_urls=["https://blogs.nvidia.com/blog/category/deep-learning/"]
    ),
    "deepmind.google": NewsSource(
        domain="deepmind.google",
        name="Google DeepMind",
        rss_urls=[],
        fallback_urls=["https://deepmind.google/discover/blog/"]
    ),
    "huggingface.co": NewsSource(
        domain="huggingface.co",
        name="Hugging Face",
        rss_urls=[],
        fallback_urls=["https://huggingface.co/blog"]
    ),
    "aws.amazon.com": NewsSource(
        domain="aws.amazon.com",
        name="AWS AI/ML",
        rss_urls=["https://aws.amazon.com/blogs/machine-learning/feed/"],
        fallback_urls=["https://aws.amazon.com/blogs/machine-learning/"]
    )
}

# Register any custom sources persisted via configuration
for domain, custom in source_config.get_custom_sources().items():
    if domain not in NEWS_SOURCES:
        NEWS_SOURCES[domain] = NewsSource(
            domain=domain,
            name=custom.get('name', domain),
            rss_urls=custom.get('rss_urls', []),
            fallback_urls=custom.get('fallback_urls', [])
        )

class SourceAdapter:
    """Base class for domain-specific content extraction"""
    
    def __init__(self, source: NewsSource):
        self.source = source
        
    def extract_content(self, url: str) -> Optional[str]:
        """Extract main content from article URL"""
        try:
            response = requests.get(url, timeout=10, headers={
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            })
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            return self._extract_main_content(soup)
            
        except Exception as e:
            logger.warning(f"Failed to extract content from {url}: {e}")
            return None
    
    def _extract_main_content(self, soup: BeautifulSoup) -> str:
        """Override in subclasses for domain-specific extraction"""
        # Generic content extraction
        for tag in soup(['script', 'style', 'nav', 'header', 'footer', 'aside']):
            tag.decompose()
            
        # Try common content selectors
        content_selectors = [
            'article', '.post-content', '.entry-content', '.content',
            '.article-body', '.story-body', 'main', '[role="main"]'
        ]
        
        for selector in content_selectors:
            content = soup.select_one(selector)
            if content:
                return content.get_text(strip=True, separator=' ')
        
        # Fallback to body text
        return soup.get_text(strip=True, separator=' ')

class SourceAdapterFactory:
    """Factory for creating domain-specific adapters"""
    
    @staticmethod
    def create_adapter(source: NewsSource) -> SourceAdapter:
        # For now, use generic adapter for all sources
        # Could add specialized adapters later for sources with unique structures
        return SourceAdapter(source)

class NewsCrawler:
    def __init__(self, days_back: int = 7, max_stories_per_source: int = 20):
        self.days_back = days_back
        self.max_stories_per_source = max_stories_per_source
        self.cutoff_date = datetime.now() - timedelta(days=days_back)
        
    def get_configured_sources(self) -> List[str]:
        """Get list of active source domains from configuration"""
        active_sources = source_config.get_active_sources()
        return [domain for domain in active_sources if domain in NEWS_SOURCES]
        
    def crawl_sources(self, source_domains: List[str]) -> List[Dict]:
        """Crawl multiple news sources and return raw stories"""
        all_stories = []
        
        for domain in source_domains:
            if domain in NEWS_SOURCES:
                source = NEWS_SOURCES[domain]
                stories = self._crawl_source(source)
                all_stories.extend(stories)
                logger.info(f"Crawled {len(stories)} stories from {source.name}")
            else:
                logger.warning(f"Unknown source domain: {domain}")
        
        return all_stories
    
    def _crawl_source(self, source: NewsSource) -> List[Dict]:
        """Crawl a single news source"""
        stories = []
        adapter = SourceAdapterFactory.create_adapter(source)
        
        # Try RSS feeds first
        for rss_url in source.rss_urls:
            try:
                feed_stories = self._parse_rss_feed(rss_url, source, adapter)
                stories.extend(feed_stories)
                if len(stories) >= self.max_stories_per_source:
                    break
            except Exception as e:
                logger.warning(f"Failed to parse RSS {rss_url}: {e}")
        
        # If no RSS or not enough stories, try HTML scraping
        if len(stories) < self.max_stories_per_source:
            for fallback_url in source.fallback_urls:
                try:
                    html_stories = self._scrape_html_page(fallback_url, source, adapter)
                    stories.extend(html_stories)
                    if len(stories) >= self.max_stories_per_source:
                        break
                except Exception as e:
                    logger.warning(f"Failed to scrape HTML {fallback_url}: {e}")
        
        return stories[:self.max_stories_per_source]
    
    def _parse_rss_feed(self, rss_url: str, source: NewsSource, adapter: SourceAdapter) -> List[Dict]:
        """Parse RSS feed and extract stories"""
        stories = []
        
        try:
            feed = feedparser.parse(rss_url)
            
            for entry in feed.entries:
                # Check if story is recent enough
                published_date = self._parse_date(entry.get('published', ''))
                if not published_date or published_date < self.cutoff_date:
                    continue
                
                # Extract story data
                story_url = entry.get('link', '')
                title = entry.get('title', '').strip()
                description = entry.get('summary', '').strip()
                
                if not story_url or not title:
                    continue
                
                # Filter out low-quality titles
                bad_titles = ['News', 'Company', 'Product', 'Safety', 'Security', 'Global Affairs', 
                             'Policy', 'Research', 'Learn More', 'Next', 'FEATURED', 'The Latest',
                             'More on the Cloud Blog', 'Tag:', 'Announcements', 'Updates']
                
                if any(bad_title in title for bad_title in bad_titles):
                    continue
                
                # Skip very short titles
                if len(title.strip()) < 10:
                    continue
                
                # Generate unique ID
                story_id = self._generate_story_id(published_date, source.domain, story_url)
                
                # Extract full content
                content = adapter.extract_content(story_url) or description
                
                story = {
                    'id': story_id,
                    'canonical_url': story_url,
                    'title': title,
                    'description': description,
                    'content': content,
                    'published_date': published_date,
                    'fetched_date': datetime.now(),
                    'source_domain': source.domain,
                    'source_name': source.name
                }
                
                stories.append(story)
                
        except Exception as e:
            logger.error(f"Error parsing RSS feed {rss_url}: {e}")
        
        return stories
    
    def _scrape_html_page(self, url: str, source: NewsSource, adapter: SourceAdapter) -> List[Dict]:
        """Scrape HTML page for article links"""
        stories = []
        
        try:
            response = requests.get(url, timeout=10, headers={
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            })
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Find article links
            article_links = self._extract_article_links(soup, url, source.domain)
            
            for link_url, title in article_links[:self.max_stories_per_source]:
                # Try to extract content
                content = adapter.extract_content(link_url)
                if not content:
                    continue
                
                # Use current time as published date (HTML scraping doesn't give us dates)
                published_date = datetime.now()
                story_id = self._generate_story_id(published_date, source.domain, link_url)
                
                story = {
                    'id': story_id,
                    'canonical_url': link_url,
                    'title': title,
                    'description': '',
                    'content': content,
                    'published_date': published_date,
                    'fetched_date': datetime.now(),
                    'source_domain': source.domain,
                    'source_name': source.name
                }
                
                stories.append(story)
                
        except Exception as e:
            logger.error(f"Error scraping HTML page {url}: {e}")
        
        return stories
    
    def _extract_article_links(self, soup: BeautifulSoup, base_url: str, domain: str) -> List[tuple]:
        """Extract article links from HTML page"""
        links = []
        
        # Common article link selectors
        selectors = [
            'a[href*="/blog/"]', 'a[href*="/news/"]', 'a[href*="/post/"]',
            'a[href*="/article/"]', 'article a', '.post-title a', '.entry-title a'
        ]
        
        seen_urls = set()
        
        for selector in selectors:
            elements = soup.select(selector)
            for element in elements:
                href = element.get('href')
                title = element.get_text(strip=True)
                
                if not href or not title:
                    continue
                
                # Convert relative URLs to absolute
                full_url = urljoin(base_url, href)
                
                # Ensure URL belongs to the same domain
                if domain not in full_url:
                    continue
                
                # Avoid duplicates
                if full_url in seen_urls:
                    continue
                
                seen_urls.add(full_url)
                links.append((full_url, title))
        
        return links
    
    def _parse_date(self, date_str: str) -> Optional[datetime]:
        """Parse various date formats"""
        if not date_str:
            return None
        
        try:
            from dateutil import parser
            parsed_date = parser.parse(date_str)
            
            # If the parsed date is timezone-naive, make it timezone-aware (UTC)
            if parsed_date.tzinfo is None:
                from datetime import timezone
                parsed_date = parsed_date.replace(tzinfo=timezone.utc)
            
            # Convert to naive datetime for comparison with cutoff_date
            return parsed_date.replace(tzinfo=None)
        except Exception as e:
            logger.debug(f"Failed to parse date '{date_str}': {e}")
            return None
    
    def _generate_story_id(self, published_date: datetime, domain: str, url: str) -> str:
        """Generate unique story ID"""
        date_str = published_date.strftime('%Y-%m-%d')
        url_hash = hashlib.md5(url.encode()).hexdigest()[:8]
        return f"{date_str}_{domain}_{url_hash}"
