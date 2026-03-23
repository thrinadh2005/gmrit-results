# Render Deployment Guide

## 🚀 Deploy GMRIT Results Scraper to Render

### ✅ Why Render?
- **Free tier available** with full functionality
- **Supports Chrome/Selenium** for web scraping
- **Easy GitHub integration**
- **Auto-deploys on push**
- **Custom domain support**
- **Background process support**

## 📋 Step-by-Step Deployment

### 1. Push to GitHub
```bash
git add .
git commit -m "Ready for Render deployment"
git remote add origin https://github.com/YOUR_USERNAME/gmrit-results.git
git push -u origin main
```

### 2. Deploy to Render

#### A) Create Account
1. Go to https://render.com
2. Sign up/login with GitHub

#### B) Create Web Service
1. Click **"New +"** → **"Web Service"**
2. **Connect** your GitHub account
3. Select **"gmrit-results"** repository
4. Configure settings:

```
Name: gmrit-results
Environment: Python 3
Root Directory: ./ (leave empty)
Build Command: pip install -r requirements.txt
Start Command: python run.py
Instance Type: Free
Plan: Free
```

#### C) Deploy
1. Click **"Create Web Service"**
2. Wait for build (2-3 minutes)
3. Get your live URL: `https://gmrit-results.onrender.com`

## 🔧 Configuration Files

### `render.yaml` (Optional)
```yaml
services:
  - type: web
    name: gmrit-results
    env: python
    plan: free
    buildCommand: pip install -r requirements.txt
    startCommand: python run.py
```

### `.renderignore`
Excludes unnecessary files from deployment

## 🌐 Access Your App

**Live URL:** `https://your-app-name.onrender.com`

**Full Features:**
- ✅ Web scraping with Chrome
- ✅ Concurrent processing
- ✅ File management
- ✅ Import/Export hall tickets
- ✅ Real-time progress tracking
- ✅ Excel generation

## 🔄 Auto-Deploys

Every push to GitHub triggers automatic redeployment:
```bash
git add .
git commit -m "Update features"
git push origin main
# Auto-deploys to Render
```

## 📊 Monitoring

- **Logs:** Available in Render dashboard
- **Metrics:** Free tier shows basic stats
- **Health Checks:** Automatic at `/`

## 🎯 Production Tips

### 1. Environment Variables
Add in Render dashboard:
```bash
PYTHON_VERSION=3.9
FLASK_ENV=production
```

### 2. Custom Domain
1. Go to **"Custom Domains"** in Render
2. Add your domain
3. Update DNS records

### 3. Scaling
- **Free:** 512MB RAM, shared CPU
- **Starter:** $7/month (better performance)
- **Standard:** $25/month (production ready)

## 🐛 Troubleshooting

### Build Fails
```bash
# Check requirements.txt
pip install -r requirements.txt --dry-run
```

### App Not Starting
```bash
# Check logs in Render dashboard
# Verify start command: python run.py
```

### Chrome Issues
Render supports Chrome/Selenium out of the box!

## 📱 Alternative Platforms

If Render doesn't work:
- **Railway.app** - Similar to Render
- **Fly.io** - Global deployment
- **DigitalOcean App Platform** - More control

## 🎉 Success!

Once deployed, you'll have:
- **Live web scraping app**
- **Full functionality**
- **Free hosting**
- **Auto-deploys**
- **Professional URL**

**Your GMRIT Results Scraper is ready for production!**
