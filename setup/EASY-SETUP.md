# 🚀 Super Simple Setup Guide

**For Non-Technical Users - No GitHub Account Required!**

## ✅ **What You'll Get:**
- Your own AI Marketing News System
- Automatic daily AI news monitoring  
- Smart newsletter generation
- Runs on your computer (private & secure)

---

## 📥 **Step 1: Download & Install Requirements**

### **Download This Software:**
1. **Get the AI News System**: [Download ZIP](https://github.com/HarrisAD/ai-marketing-news/archive/refs/heads/main.zip)
2. **Extract the ZIP file** to your Desktop
3. **Open the new folder** and then open the **`setup`** folder inside it
4. **Install Python**: [Download here](https://www.python.org/downloads/)  
   - ✅ **Important**: Check "Add Python to PATH" during installation
5. **Install Node.js**: [Download here](https://nodejs.org/)
   - Choose "LTS" version (recommended)

### **Get Your OpenAI API Key:**
6. **Sign up at OpenAI**: [Get API Key](https://platform.openai.com/api-keys)
7. **Create new key** and copy it (starts with `sk-...`)

---

## ⚡ **Step 2: One-Click Setup**

### **For Windows:**
1. **Open the `setup` folder**
2. **Double-click**: `setup.bat`
3. **Wait for installation** (2-3 minutes)
4. **Optional**: open `backend/.env` if you want to hard-code your key now. Otherwise you can paste it into the dashboard when prompted after launch.

### **For Mac:**
1. **Double-click** `Mac-Setup.command` inside the `setup` folder
2. **If macOS blocks it**, right-click (or control-click) the file → **Open** → **Open**. You can also go to **System Settings → Privacy & Security** and click **Open Anyway** if the warning appears.
3. **Wait for installation** (2-3 minutes)
4. **Optional**: edit `backend/.env` to add the key now, or paste it into the dashboard later.

### **For Linux:**
1. **Open Terminal**, then `cd` into the `setup` folder
2. **Run** `chmod +x setup.sh` (first time only)
3. **Run** `./setup.sh`
4. **Optional**: edit `backend/.env` to add the key now, or paste it into the dashboard later.

---

## 🎉 **Step 3: Start Your AI News System**

### **For Windows:**
- **Double-click** `start.bat` inside the `setup` folder

### **For Mac:**
- **Double-click** `Start-System.command`
  - macOS may ask you to allow it the first time (choose “Open”)

### **For Linux:**
- From the `setup` folder run: `./start.sh`

**Your AI News System will open automatically!** 🎊

---

## 📱 **How to Use:**

1. **Dashboard Opens**: http://localhost:3000
2. **Add your OpenAI key** using the blue "OpenAI API Key" card (paste the `sk-...` key and press Save)
3. **Click "Refresh Stories"** to get latest AI news
4. **Wait 5-10 minutes** for AI analysis  
5. **Browse high-score stories** (80+ marketing relevance)
6. **Create newsletters** from selected stories

---

## 💰 **Costs:**
- **Software**: FREE
- **OpenAI Usage**: ~$5-20/month (depends on how much you use)

---

## 🆘 **Need Help?**

### **Common Issues:**

**"Python not found"**
- Download Python from link above
- Make sure to check "Add to PATH"

**"Node.js not found"**  
- Download Node.js from link above
- Restart your computer after installing

**"No stories loading"**
- Check your OpenAI API key in `backend/.env`
- Make sure you have OpenAI credits

**"Can't open files"**
- Right-click files → "Open with" → Notepad/TextEdit

---

## 🔄 **Daily Use:**
- **Double-click** `setup/start.bat` (Windows), `setup/Start-System.command` (Mac), or run `setup/start.sh` (Linux)
- **Check dashboard** for new stories
- **Create newsletters** as needed
- **Close terminal windows** to stop

---

**That's it! You now have your own AI Marketing News System! 🚀**
