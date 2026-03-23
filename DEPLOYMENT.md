# Vercel Deployment Guide

## ⚠️ Important Limitations

**GMRIT Results Scraper requires Chrome/Selenium for web scraping, which cannot run in Vercel's serverless environment.**

## 🚀 Vercel Deployment (Limited Version)

### What Works on Vercel:
- ✅ Web Interface
- ✅ Hall Ticket Management (Add/Remove/Import/Export)
- ✅ UI and Navigation
- ✅ Basic Status Display

### What Doesn't Work on Vercel:
- ❌ Actual Web Scraping (requires Chrome)
- ❌ PDF Generation
- ❌ Excel Generation
- ❌ File Downloads

## 📋 Deployment Steps

### 1. Install Vercel CLI
```bash
npm install -g vercel
```

### 2. Deploy to Vercel
```bash
vercel --prod
```

### 3. Configuration
- The app will deploy with limited functionality
- Users can manage hall tickets but cannot scrape
- Shows message: "Full scraping requires local deployment"

## 🏠 Alternative: Full Local Deployment

For complete functionality, deploy locally:

### Option 1: Home Server
```bash
# On your server/VPS
pip install -r requirements.txt
python run.py
```

### Option 2: Docker
```dockerfile
FROM python:3.9-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
RUN apt-get update && apt-get install -y wget gnupg unzip
RUN wget -q -O - https://dl.google.com/linux/linux_signing_key.pub | apt-key add -
RUN echo "deb [arch=amd64] http://dl.google.com/linux/chrome/deb/ stable main" > /etc/apt/sources.list.d/google-chrome.list
RUN apt-get update && apt-get install -y google-chrome-stable
EXPOSE 5000
CMD ["python", "run.py"]
```

### Option 3: Cloud Services with Browser Support
- **Render.com** - Supports background processes
- **Railway.app** - Has browser support
- **DigitalOcean** - Full VPS control
- **AWS EC2** - Complete control

## 🎯 Recommended Deployment

### For Production Use:
1. **Deploy Locally** or use **VPS** (DigitalOcean, AWS)
2. **Use Docker** for easy deployment
3. **Configure Domain** and SSL
4. **Set up Monitoring** and backups

### For Demo/Portfolio:
1. **Deploy to Vercel** (limited functionality)
2. **Add Notice** about full local deployment
3. **Include GitHub link** for full version

## 🔧 Vercel Configuration Files

- `vercel.json` - Vercel deployment settings
- `api/index.py` - Serverless function (limited version)
- `requirements-vercel.txt` - Minimal dependencies for Vercel

## 📝 Deployment Commands

```bash
# Deploy to Vercel (limited)
vercel --prod

# Deploy locally (full functionality)
python run.py

# Deploy with Docker
docker build -t gmrit-scraper .
docker run -p 5000:5000 gmrit-scraper
```

## 🌐 Access Options

- **Vercel**: `https://your-app.vercel.app` (limited)
- **Local**: `http://localhost:5000` (full functionality)
- **VPS**: `http://your-server-ip:5000` (full functionality)
