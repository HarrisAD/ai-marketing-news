# 🚀 One-Click Deployment Guide

## Deploy to Railway (Recommended)

[![Deploy on Railway](https://railway.app/button.svg)](https://railway.app/deploy?referrer=github&template=https://github.com/HarrisAD/ai-marketing-news)

### Quick Setup (3 minutes):

1. **Click the deploy button above**
2. **Connect your GitHub account** (Railway will fork this repo)
3. **Add environment variables**:
   - `OPENAI_API_KEY`: Get from https://platform.openai.com/api-keys
   - `PORT`: `8000` (Railway will auto-set this)
4. **Click "Deploy"**
5. **Wait 3-5 minutes** for build and deployment

Your AI Marketing News System will be live at: `https://yourapp.up.railway.app`

### What You Get:
- ✅ Automated daily AI news crawling
- ✅ GPT-4o-mini story scoring for marketing relevance
- ✅ Professional newsletter generation
- ✅ Web dashboard for story management
- ✅ Automatic HTTPS and domain
- ✅ Free hosting (within Railway limits)

### Cost Breakdown:
- **Railway Hosting**: FREE (within $5/month credit)
- **OpenAI API**: ~$5-20/month (depending on usage)
- **Total**: $5-20/month

### After Deployment:
1. Visit your app URL
2. Click "Refresh Stories" to crawl initial news
3. Wait 5-10 minutes for AI analysis
4. Create your first newsletter!

### Daily Automation:
- News crawls automatically at 8:30 AM London time
- Stories are scored and deduplicated
- View your dashboard anytime for latest updates

---

## Alternative: Manual Railway Setup

If the one-click button doesn't work:

1. **Fork this repository** to your GitHub account
2. **Sign up at [Railway](https://railway.app)**
3. **Connect your GitHub** and select this repository
4. **Add environment variables**:
   ```
   OPENAI_API_KEY=your_openai_api_key_here
   OPENAI_MODEL=gpt-4o-mini
   PORT=8000
   HOST=0.0.0.0
   ```
5. **Deploy** and wait for completion

---

## Local Development Setup

If you prefer to run locally:

### Prerequisites:
- Python 3.8+
- Node.js 18+
- OpenAI API key

### Backend Setup:
```bash
cd backend
pip install -r requirements.txt
cp .env.example .env
# Edit .env with your OpenAI API key
cd src && python -m uvicorn main:app --reload
```

### Frontend Setup:
```bash
cd frontend
npm install
npm run dev
```

Visit: http://localhost:3000

---

## Troubleshooting

### Deployment Issues:
- **Build fails**: Check that all required files are committed to git
- **App crashes**: Verify your OpenAI API key is valid
- **Slow loading**: Initial story crawling takes 5-10 minutes

### Getting Help:
- Check Railway logs for error details
- Ensure OpenAI API key has sufficient credits
- Contact support if issues persist

### Railway Limits:
- **Free tier**: $5/month credit, auto-sleep after 30min idle
- **Upgrade**: Remove limits with Pro plan ($5/month)

---

## Features Overview

### 🔍 News Sources (17+ sites monitored):
- OpenAI, Anthropic, Google AI, Microsoft AI
- Meta AI, Hugging Face, DeepMind
- TechCrunch AI, VentureBeat AI, and more

### 📊 AI Scoring System:
- **Relevance** (35%): Marketing impact
- **Impact** (25%): Significance of change
- **Adoption** (15%): Availability/actionability  
- **Urgency** (15%): Time-sensitivity
- **Credibility** (10%): Source reliability

### 📧 Newsletter Generation:
- Professional markdown format
- Prioritized by AI scores
- Marketing-focused insights
- Ready for email/web publishing

### 🎯 Marketing Categories:
Models, Ads/Targeting, Creative Tools, Analytics, Automation, Personalization, Voice/Audio, Video, Search/SEO, E-commerce, Social Media, Email Marketing, Content Marketing, Customer Service, Data/Privacy, Emerging Tech

---

**Ready to deploy? Click the Railway button at the top! 🚀**