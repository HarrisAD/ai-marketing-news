import json
import logging
import time
from typing import Dict, List, Optional
from openai import OpenAI
from models.story import Story, StoryTag
from services.config import settings

logger = logging.getLogger(__name__)

class LLMService:
    def __init__(self):
        self.client = OpenAI(api_key=settings.openai_api_key)
        self.model = settings.openai_model
    
    def score_story(self, story_dict: Dict) -> Dict:
        """Score a story for marketing relevance and extract metadata"""
        
        # Create prompt for story analysis
        prompt = self._create_scoring_prompt(story_dict)
        
        try:
            # Add rate limiting to prevent 429 errors
            time.sleep(0.5)  # Wait 500ms between API calls
            
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": self._get_scoring_system_prompt()},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.1,
                max_tokens=1000
            )
            
            # Parse the JSON response
            content = response.choices[0].message.content.strip()
            
            # Log the raw response for debugging
            logger.debug(f"Raw OpenAI response: {content[:200]}...")
            
            # Try to extract JSON if it's wrapped in markdown code blocks
            if content.startswith('```json'):
                content = content.split('```json')[1].split('```')[0].strip()
            elif content.startswith('```'):
                content = content.split('```')[1].split('```')[0].strip()
            
            # Additional cleaning for common issues
            if not content:
                raise ValueError("Empty response from OpenAI")
            
            # Try to find JSON object in the response
            if '{' in content and '}' in content:
                start = content.find('{')
                end = content.rfind('}') + 1
                content = content[start:end]
            
            result = json.loads(content)
            
            # Update story dict with AI analysis
            story_dict.update({
                'score': result.get('overall_score', 0),
                'marketer_relevance': result.get('marketer_relevance', []),
                'action_hint': result.get('action_hint', ''),
                'tags': result.get('tags', []),
                'relevance_score': result.get('relevance_score', 0),
                'impact_score': result.get('impact_score', 0),
                'adoption_score': result.get('adoption_score', 0),
                'urgency_score': result.get('urgency_score', 0),
                'credibility_score': result.get('credibility_score', 0)
            })
            
            logger.info(f"Scored story '{story_dict['title']}' with score {result.get('overall_score', 0)}")
            return story_dict
            
        except json.JSONDecodeError as e:
            logger.error(f"JSON parsing failed for story '{story_dict.get('title', 'Unknown')}': {e}")
            logger.error(f"Raw content was: {content[:500] if 'content' in locals() else 'No content captured'}")
            # Return story with default/empty scores
        except Exception as e:
            logger.error(f"Failed to score story '{story_dict.get('title', 'Unknown')}': {e}")
            # Return story with default/empty scores
            story_dict.update({
                'score': 0,
                'marketer_relevance': [],
                'action_hint': '',
                'tags': [],
                'relevance_score': 0,
                'impact_score': 0,
                'adoption_score': 0,
                'urgency_score': 0,
                'credibility_score': 0
            })
            return story_dict
    
    def _get_scoring_system_prompt(self) -> str:
        """System prompt defining the marketing relevance scoring criteria"""
        return """You are an expert marketing technology analyst. Your job is to evaluate AI news stories for their relevance to marketing professionals and score them 0-100.

SCORING CRITERIA (weighted):
1. RELEVANCE (35%): How directly does this impact marketing activities?
   - 90-100: Direct impact on ad targeting, creative generation, or campaign measurement
   - 70-89: Strong implications for marketing tools and strategies
   - 50-69: Moderate relevance to marketing professionals
   - 30-49: Tangential connection to marketing
   - 0-29: Little to no marketing relevance

2. IMPACT (25%): How significant is the potential change?
   - 90-100: Game-changing capability that transforms marketing
   - 70-89: Major improvement in existing marketing processes
   - 50-69: Noticeable enhancement to marketing capabilities
   - 30-49: Minor improvement
   - 0-29: Minimal impact

3. ADOPTION (15%): How available/actionable is this?
   - 90-100: Generally available, marketers can use now
   - 70-89: Limited availability, some can access
   - 50-69: Beta/preview access
   - 30-49: Research/demo phase
   - 0-29: Early research, not accessible

4. URGENCY (15%): How time-sensitive is this for marketers?
   - 90-100: Immediate action required, competitive advantage
   - 70-89: Should test/evaluate soon
   - 50-69: Worth monitoring and planning
   - 30-49: General awareness needed
   - 0-29: No urgency

5. CREDIBILITY (10%): How reliable is this information?
   - 90-100: Official announcement from major company
   - 70-89: Credible source with clear details
   - 50-69: Reliable source, some details unclear
   - 30-49: Some uncertainty about details
   - 0-29: Rumor or unverified information

MARKETING CATEGORIES:
- Models: New AI models for content/targeting
- Ads/Targeting: Advertising and audience targeting
- Creative Tools: Content and creative generation
- Analytics: Data analysis and insights
- Automation: Marketing automation and workflows
- Personalization: Customer personalization
- Voice/Audio: Voice and audio marketing
- Video: Video marketing and production
- Search/SEO: Search optimization and discovery
- E-commerce: Online retail and shopping
- Social Media: Social platform marketing
- Email Marketing: Email campaigns and automation
- Content Marketing: Content strategy and creation
- Customer Service: Support and engagement
- Data/Privacy: Data handling and privacy
- Emerging Tech: New technologies affecting marketing

Return your analysis as JSON with this exact structure:
{
  "overall_score": <0-100>,
  "relevance_score": <0-100>,
  "impact_score": <0-100>,
  "adoption_score": <0-100>,
  "urgency_score": <0-100>,
  "credibility_score": <0-100>,
  "marketer_relevance": ["brief bullet point 1", "brief bullet point 2"],
  "action_hint": "specific suggestion for marketers",
  "tags": ["tag1", "tag2"]
}"""
    
    def _create_scoring_prompt(self, story: Dict) -> str:
        """Create prompt for scoring a specific story"""
        # Truncate content if too long
        content = story.get('content', '')
        if len(content) > 2000:
            content = content[:2000] + "..."
        
        return f"""Analyze this AI news story for marketing relevance:

TITLE: {story.get('title', '')}

SOURCE: {story.get('source_name', '')} ({story.get('source_domain', '')})

DESCRIPTION: {story.get('description', '')}

CONTENT: {content}

PUBLISHED: {story.get('published_date', '')}

Provide a detailed analysis focusing on how this affects marketing professionals, what actions they should take, and assign appropriate tags from the provided categories."""
    
    def generate_newsletter(self, stories: List[Dict], editorial_instructions: str = "") -> str:
        """Generate newsletter content from selected stories"""
        
        if not stories:
            return "No stories selected for newsletter."
        
        # Sort stories by score (highest first)
        sorted_stories = sorted(stories, key=lambda x: x.get('score', 0), reverse=True)
        
        # Create newsletter prompt
        prompt = self._create_newsletter_prompt(sorted_stories, editorial_instructions)
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": self._get_newsletter_system_prompt()},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3,
                max_tokens=3000
            )
            
            newsletter_content = response.choices[0].message.content
            logger.info(f"Generated newsletter with {len(stories)} stories")
            return newsletter_content
            
        except Exception as e:
            logger.error(f"Failed to generate newsletter: {e}")
            return f"Error generating newsletter: {str(e)}"
    
    def _get_newsletter_system_prompt(self) -> str:
        """System prompt for newsletter generation"""
        return """You are an expert marketing newsletter writer specializing in AI technology. 

Your job is to create engaging, informative newsletters that help marketing professionals stay current with AI developments that matter to their work.

STYLE GUIDELINES:
- Professional but approachable tone
- Focus on practical implications for marketers
- Include specific action items when relevant
- Use clear, scannable formatting with headers
- Prioritize high-scoring stories
- Provide context for why each story matters
- Include brief analysis of trends when appropriate

STRUCTURE:
1. Brief opening that sets the week's theme
2. Top stories with analysis
3. Quick hits for lower-priority items
4. Closing thoughts or trends observation

FORMAT: Return clean Markdown that's ready for email or web publishing."""
    
    def _create_newsletter_prompt(self, stories: List[Dict], editorial_instructions: str) -> str:
        """Create prompt for newsletter generation"""
        
        # Format stories for the prompt
        story_summaries = []
        for i, story in enumerate(stories[:10], 1):  # Limit to top 10 stories
            summary = f"""
STORY {i} (Score: {story.get('score', 0)}/100)
Title: {story['title']}
Source: {story.get('source_name', '')}
Key Points: {'; '.join(story.get('marketer_relevance', []))}
Action: {story.get('action_hint', '')}
Tags: {', '.join(story.get('tags', []))}
URL: {story['canonical_url']}
"""
            story_summaries.append(summary)
        
        prompt = f"""Create a marketing newsletter from these AI news stories:

{chr(10).join(story_summaries)}

EDITORIAL INSTRUCTIONS: {editorial_instructions or "Create an engaging newsletter focusing on practical implications for marketing professionals."}

Focus on the highest-scoring stories and provide actionable insights for marketing professionals."""
        
        return prompt