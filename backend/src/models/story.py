from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, Field
from enum import Enum

class StoryTag(str, Enum):
    MODELS = "Models"
    ADS_TARGETING = "Ads/Targeting"
    CREATIVE_TOOLS = "Creative Tools"
    ANALYTICS = "Analytics"
    AUTOMATION = "Automation"
    PERSONALIZATION = "Personalization"
    VOICE_AUDIO = "Voice/Audio"
    VIDEO = "Video"
    SEARCH_SEO = "Search/SEO"
    ECOMMERCE = "E-commerce"
    SOCIAL_MEDIA = "Social Media"
    EMAIL_MARKETING = "Email Marketing"
    CONTENT_MARKETING = "Content Marketing"
    CUSTOMER_SERVICE = "Customer Service"
    DATA_PRIVACY = "Data/Privacy"
    EMERGING_TECH = "Emerging Tech"

class Story(BaseModel):
    id: str = Field(..., description="Unique identifier: date_domain_hash")
    canonical_url: str = Field(..., description="Primary URL for this story")
    title: str = Field(..., description="Story title")
    description: str = Field(default="", description="Story description/summary")
    content: str = Field(default="", description="Full article content")
    published_date: datetime = Field(..., description="When the story was published")
    fetched_date: datetime = Field(default_factory=datetime.now, description="When we fetched this story")
    source_domain: str = Field(..., description="Domain of the source (e.g., openai.com)")
    source_name: str = Field(..., description="Human-readable source name")
    
    # AI-generated fields
    score: Optional[int] = Field(None, ge=0, le=100, description="Marketing relevance score 0-100")
    marketer_relevance: List[str] = Field(default_factory=list, description="How this affects marketers")
    action_hint: str = Field(default="", description="Suggested action for marketers")
    tags: List[StoryTag] = Field(default_factory=list, description="Categorization tags")
    
    # Scoring breakdown
    relevance_score: Optional[int] = Field(None, ge=0, le=100, description="Relevance component")
    impact_score: Optional[int] = Field(None, ge=0, le=100, description="Impact component")
    adoption_score: Optional[int] = Field(None, ge=0, le=100, description="Adoption component")
    urgency_score: Optional[int] = Field(None, ge=0, le=100, description="Urgency component")
    credibility_score: Optional[int] = Field(None, ge=0, le=100, description="Credibility component")
    
    # Deduplication
    similar_stories: List[str] = Field(default_factory=list, description="IDs of similar stories")
    is_canonical: bool = Field(default=True, description="Is this the primary version?")
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }

class NewsletterRequest(BaseModel):
    date_from: datetime
    date_to: datetime
    min_score: int = Field(default=60, ge=0, le=100)
    selected_story_ids: List[str] = Field(default_factory=list)
    editorial_instructions: str = Field(default="", description="Tone, theme, opener instructions")
    max_stories: int = Field(default=10, ge=1, le=50)

class NewsletterResponse(BaseModel):
    newsletter_id: str
    markdown_content: str
    story_count: int
    generated_date: datetime
    stories_used: List[str]