# AI Marketing News System

An automated AI news monitoring and newsletter generation system designed specifically for marketers.

## 🚀 One-Click Deployment

[![Deploy on Railway](https://railway.app/button.svg)](https://railway.app/template/gQJA2Y?referralCode=HarrisAD)

**Quick Deploy (2 minutes):**
1. Click the deploy button above
2. Add your OpenAI API key
3. Wait for deployment to complete
4. Start using your AI marketing news system!

**Cost:** FREE on Railway (within $5/month credit) + OpenAI usage (~$5-20/month)

[📖 **Detailed Deployment Guide**](./DEPLOY.md)

---

## 🚀 Local Development Setup

### Prerequisites
- **Python 3.8+** 
- **Node.js 16+**
- **OpenAI API Key** (get one at [platform.openai.com](https://platform.openai.com/api-keys))

### 1. Setup Backend

```bash
# Clone and navigate to project
cd ai-marketing-news/backend

# Install Python dependencies
pip install -r requirements.txt

# Copy environment template and add your OpenAI API key
cp .env.example .env
# Edit .env file with your OPENAI_API_KEY

# Start backend server
cd src
python -m uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### 2. Setup Frontend

```bash
# In a new terminal, navigate to frontend
cd ai-marketing-news/frontend

# Install Node.js dependencies
npm install

# Start development server
npm run dev
```

### 3. Access the Application

- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs

## ✨ Features

### 🤖 Smart News Crawling
- **17+ AI News Sources**: OpenAI, Anthropic, Microsoft, Google, Meta, MIT Tech Review, and more
- **Intelligent Extraction**: Domain-specific content parsing for accurate story extraction
- **Automatic Deduplication**: Detects and handles duplicate stories across sources

### 🎯 AI-Powered Scoring
- **Marketing Relevance Scoring**: 0-100 score based on marketing impact
- **5-Factor Analysis**: Relevance, Impact, Adoption, Urgency, Credibility
- **Action Hints**: Specific suggestions for marketing professionals
- **Smart Categorization**: Auto-tagging with marketing-specific categories

### 📰 Newsletter Generation
- **Custom Newsletters**: Generate from selected stories or date ranges
- **Editorial Control**: Add tone, theme, and style instructions
- **Multiple Formats**: Markdown export for easy sharing
- **Story Analytics**: Track performance and engagement metrics

### 🔄 Automated Updates
- **Daily Scheduling**: Automatic updates at configurable times
- **Manual Refresh**: On-demand story updates
- **Background Processing**: Non-blocking AI analysis

## 📁 Project Structure

```
ai-marketing-news/
├── backend/                  # Python FastAPI Backend
│   ├── src/
│   │   ├── api/             # REST API endpoints
│   │   ├── models/          # Pydantic data models
│   │   ├── services/        # Business logic
│   │   └── main.py          # FastAPI application
│   ├── data/                # JSONL data storage
│   ├── logs/                # Application logs
│   └── requirements.txt     # Python dependencies
├── frontend/                # React TypeScript Frontend
│   ├── src/
│   │   ├── components/      # Reusable UI components
│   │   ├── pages/          # Main application pages
│   │   ├── services/       # API client
│   │   └── types/          # TypeScript definitions
│   └── package.json        # Node.js dependencies
└── docs/                   # Documentation
```

## ⚙️ Configuration

### Environment Variables (.env)

```bash
# Required
OPENAI_API_KEY=your_openai_api_key_here

# Optional (with defaults)
OPENAI_MODEL=gpt-4o-mini
DATA_DIR=./data
LOGS_DIR=./logs
HOST=0.0.0.0
PORT=8000
CRON_TIME=08:30
MIN_SCORE_DEFAULT=60
TIMEZONE=Europe/London
CRAWLER_DAYS_BACK=7
MAX_STORIES_PER_SOURCE=20
RUN_SOURCES=openai.com,anthropic.com,microsoft.com,google.com,meta.com
```

### News Sources (Built-in)

**Major AI Companies:**
- OpenAI, Anthropic, Microsoft AI, Google AI, Meta AI
- Perplexity, Claude, GPT updates

**Marketing & Tech Publications:**
- Marketing AI Institute, MIT Technology Review
- The Economist Technology, Forbes AI
- Fortune AI, One Useful Thing

**Academic & Research:**
- Research papers and announcements
- Industry trend analysis

## 🛠️ API Reference

### Stories Endpoints

```http
GET /api/stories                    # List stories with filters
GET /api/stories/{id}              # Get specific story
POST /api/refresh                   # Manual story refresh
GET /api/sources                    # Available news sources
GET /api/tags                       # Story categorization tags
GET /api/stats                      # System statistics
```

### Newsletter Endpoints

```http
POST /api/newsletters/render        # Generate newsletter
GET /api/newsletters               # List newsletters
GET /api/newsletters/{id}          # Get newsletter content
GET /api/newsletters/{id}/markdown # Download as Markdown
GET /api/newsletters/{id}/stories  # Stories used in newsletter
```

### Story Filtering Parameters

```javascript
{
  min_score: 80,              // Minimum relevance score
  source_domain: "openai.com", // Filter by source
  days_back: 7,               // Time range
  limit: 50,                  // Maximum results
  canonical_only: true        // Exclude duplicates
}
```

### Newsletter Generation

```javascript
{
  date_from: "2024-01-01T00:00:00Z",
  date_to: "2024-01-07T23:59:59Z",
  min_score: 80,
  selected_story_ids: ["story1", "story2"],
  editorial_instructions: "Focus on B2B marketing implications",
  max_stories: 10
}
```

## 📊 Scoring Rubric

Stories are scored 0-100 using weighted criteria:

| Criteria | Weight | Description |
|----------|--------|-------------|
| **Relevance** | 35% | Direct impact on marketing activities |
| **Impact** | 25% | Magnitude of potential change |
| **Adoption** | 15% | Current availability vs. research phase |
| **Urgency** | 15% | Time-sensitivity for action |
| **Credibility** | 10% | Source quality and verification |

### Score Ranges
- **90-100**: Excellent - Immediate marketing impact
- **80-89**: High - Strong marketing relevance  
- **70-79**: Good - Worth monitoring
- **60-69**: Moderate - General awareness
- **0-59**: Low - Limited marketing relevance

## 🔧 Development

### Backend Development

```bash
cd backend

# Install dev dependencies
pip install -r requirements.txt

# Run with auto-reload
cd src
python -m uvicorn main:app --reload --port 8000

# Run tests
python -m pytest

# Type checking
mypy src/
```

### Frontend Development

```bash
cd frontend

# Install dependencies
npm install

# Start dev server
npm run dev

# Build for production
npm run build

# Type checking
npm run typecheck

# Linting
npm run lint
```

### Adding New News Sources

1. **Add source definition** in `backend/src/services/sources.py`:

```python
NEWS_SOURCES["newdomain.com"] = NewsSource(
    domain="newdomain.com",
    name="New Source Name", 
    rss_urls=["https://newdomain.com/feed.xml"],
    fallback_urls=["https://newdomain.com/news"]
)
```

2. **Add domain to config** in `.env`:

```bash
RUN_SOURCES=openai.com,anthropic.com,newdomain.com
```

3. **Test extraction** by running a manual refresh

## 📈 Usage Guide

### Dashboard
- **System Overview**: Story counts, newsletter stats, score distribution
- **Recent Stories**: Quick view of high-impact stories
- **Quick Actions**: Direct links to key features

### Story Management
- **Browse & Filter**: Search by score, source, date, tags
- **Bulk Selection**: Select multiple stories for newsletters
- **Detailed View**: Full content, score breakdown, action hints

### Newsletter Creation
- **Date Range Selection**: Choose story timeframe
- **Story Curation**: Auto-select or manual selection
- **Editorial Control**: Add instructions for tone/style
- **Instant Preview**: See generated content before download

### Automation
- **Daily Updates**: Configurable scheduled crawling
- **Smart Deduplication**: Automatic duplicate detection
- **Background Processing**: Non-blocking AI analysis

## 🐛 Troubleshooting

### Common Issues

**"No stories loading"**
```bash
# Check if OpenAI API key is configured
curl http://localhost:8000/health

# Manually trigger refresh
curl -X POST http://localhost:8000/api/refresh
```

**"Failed to generate newsletter"**
- Verify OpenAI API key has sufficient credits
- Check selected stories aren't empty
- Review logs in `backend/logs/`

**"Frontend won't start"**
```bash
# Clear node modules and reinstall
rm -rf node_modules package-lock.json
npm install
```

**"Backend errors"**
```bash
# Check Python dependencies
pip install -r requirements.txt

# Verify data directories exist
ls -la backend/data backend/logs
```

### Performance Optimization

**For Large Story Collections:**
- Increase `limit` parameter for API calls
- Use date range filters to reduce dataset
- Consider increasing `max_stories` for newsletters

**For Slow Generation:**
- Reduce `max_stories` in newsletter requests
- Check OpenAI API response times
- Monitor system resources

## 🔒 Security & Privacy

### API Key Security
- Never commit `.env` file to version control
- Rotate OpenAI API keys regularly
- Monitor usage at platform.openai.com

### Data Privacy
- Stories stored locally in JSONL format
- No personal data collection
- Source URLs and metadata only

### Network Security
- Application runs on localhost by default
- CORS configured for local development
- No external data transmission except to news sources and OpenAI

## 📄 License

This project is intended for internal use and evaluation of AI news monitoring systems.

## 🤝 Support

For issues or feature requests:
1. Check the troubleshooting section above
2. Review API documentation at http://localhost:8000/docs
3. Check application logs in `backend/logs/`

---

**Built with:** FastAPI, React, TypeScript, OpenAI GPT-4o-mini, Tailwind CSS