# 🚀 Getting Started - AI Marketing News System

This is your complete guide to setting up and running the AI Marketing News System.

## 📋 What You'll Need

1. **OpenAI API Key** (required)
   - Go to [platform.openai.com/api-keys](https://platform.openai.com/api-keys)
   - Create account or sign in
   - Click "Create new secret key"
   - Copy the key (starts with `sk-...`)

2. **Python 3.8+** 
   - Download from [python.org](https://python.org/downloads/)
   - ✅ **IMPORTANT**: Check "Add Python to PATH" during installation

3. **Node.js 16+**
   - Download from [nodejs.org](https://nodejs.org/)

## ⚡ Quick Setup (Recommended)

### Option 1: Automated Setup

Download the project first: [Grab the ZIP directly](https://github.com/HarrisAD/ai-marketing-news/archive/refs/heads/main.zip), extract it, then open the new folder.

```bash
# Move into the setup folder
cd setup

# Run the setup script
./setup.sh

# Follow the prompts to add your OpenAI API key
```

💡 **macOS shortcut:** you can double-click `Mac-Setup.command` in the `setup` folder instead of using Terminal.

When the dashboard opens for the first time, use the **OpenAI API Key** card to paste your `sk-...` key. It is stored securely on your machine and used for all future requests.

### Option 2: Manual Setup

```bash
# Backend setup
cd backend
pip install -r requirements.txt
cp .env.example .env
# Edit .env file with your OpenAI API key

> 💡 Alternatively, you can paste the key later into the dashboard's **OpenAI API Key** card and the system will store it for you.

# Frontend setup  
cd ../frontend
npm install
```

## 🏃‍♂️ Running the System

### Start Backend (Terminal 1)
```bash
# From the project root
./setup/start-backend.sh
```
✅ Backend will be available at http://localhost:8000

### Start Frontend (Terminal 2)
```bash  
./setup/start-frontend.sh
```
✅ Frontend will be available at http://localhost:3000

## 🎯 Your First Steps

### 1. Open the Application
- Go to http://localhost:3000
- You should see the AI Marketing News dashboard

### 2. Load Some Stories
- Click "Refresh Stories" button on the dashboard
- Wait 30-60 seconds for stories to be crawled and scored
- Stories will appear in the dashboard

### 3. Explore Features
- **Dashboard**: Overview of stories and stats
- **Stories**: Browse and filter all stories
- **Create Newsletter**: Generate custom newsletters
- **Newsletters**: View past newsletters

### 4. Create Your First Newsletter
- Go to "Create Newsletter"
- Select date range (default: last 7 days)
- Choose minimum score (80+ recommended)
- Add editorial instructions (optional)
- Click "Generate Newsletter"
- Download as Markdown

## 🔧 Configuration

### Environment Variables (backend/.env)

```bash
# Optional - Add your actual API key here or use the dashboard form
OPENAI_API_KEY=sk-your_actual_key_here

# Optional - Default values work fine if you don't set them here
OPENAI_MODEL=gpt-4o-mini
CRON_TIME=08:30
MIN_SCORE_DEFAULT=80
```

### Available News Sources

The system automatically monitors:
- **AI Companies**: OpenAI, Anthropic, Microsoft, Google, Meta
- **Tech Publications**: MIT Technology Review, Forbes, Fortune
- **Marketing**: Marketing AI Institute, One Useful Thing
- **Business**: The Economist, Harvard Business Review

## 📊 Understanding Scores

Stories are scored 0-100 for marketing relevance:

- **90-100**: 🔥 Excellent - Take immediate action
- **80-89**: ⭐ High - Strong marketing impact
- **70-79**: 👍 Good - Worth monitoring  
- **60-69**: 📝 Moderate - General awareness
- **0-59**: 📊 Low - Limited relevance

## 🤖 How It Works

1. **Crawling**: System fetches news from 17+ AI sources
2. **Scoring**: GPT-4o analyzes each story for marketing relevance
3. **Deduplication**: Similar stories are merged automatically
4. **Categorization**: Stories are tagged by marketing category
5. **Newsletters**: AI generates custom newsletters from selected stories

## 🎨 Key Features

### Smart Story Scoring
- 5-factor analysis: Relevance, Impact, Adoption, Urgency, Credibility
- Marketing-specific action hints
- Automatic categorization

### Flexible Newsletter Generation
- Date range selection
- Score-based filtering
- Editorial instruction support
- Instant Markdown export

### Professional Interface
- Clean, modern design
- Advanced filtering options
- Bulk story selection
- Mobile-responsive

## 🔍 Troubleshooting

### "No stories loading"
1. Check your OpenAI API key in `backend/.env`
2. Verify internet connection
3. Check API credits at platform.openai.com
4. Try clicking "Refresh Stories" again

### "Backend won't start"
```bash
# Check Python installation
python3 --version

# Reinstall dependencies
cd backend
pip install -r requirements.txt
```

### "Frontend won't start"
```bash
# Check Node.js installation
node --version

# Clear and reinstall
cd frontend
rm -rf node_modules package-lock.json
npm install
```

### "Newsletter generation fails"
1. Ensure stories are selected
2. Check OpenAI API credits
3. Verify API key has sufficient permissions
4. Try with fewer stories (reduce max_stories)

## 💡 Pro Tips

### For Better Results
- Use score filter 80+ for high-impact stories
- Add specific editorial instructions for targeted newsletters
- Check the "Marketing Impact" section in each story for key insights

### For Performance
- Limit story count to 50-100 for faster loading
- Use date ranges to focus on recent content
- Clear browser cache if interface seems slow

### For Customization
- Edit news sources in `backend/src/services/sources.py`
- Modify scoring criteria in `backend/src/services/llm_service.py`
- Customize UI colors in `frontend/src/index.css`

## 🆘 Need Help?

1. **Check the logs**: Look in `backend/logs/` for error messages
2. **Verify configuration**: Ensure `.env` file has correct API key
3. **Test API**: Visit http://localhost:8000/health to check backend status
4. **Review documentation**: See `README.md` for detailed technical info

## 🎉 Success Indicators

You'll know everything is working when:
- ✅ Stories appear in the dashboard after refresh
- ✅ Story scores are visible (should be 0-100)
- ✅ Newsletter generation completes successfully
- ✅ Downloaded newsletters contain formatted content

## 📈 Next Steps

Once you have the system running:
1. Set up automated daily updates (runs at 8:30 AM by default)
2. Customize news sources for your specific interests
3. Create regular newsletters for your team
4. Monitor high-scoring stories for competitive intelligence

---

**Questions?** Review the full documentation in `README.md` or check the API docs at http://localhost:8000/docs
