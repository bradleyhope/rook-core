# ROOK Render Deployment Guide

## Overview

This guide will help you deploy ROOK to Render.com for production hosting.

**What You're Deploying:**
- ROOK AI investigative journalist chat interface
- FastAPI backend with Pinecone memory integration
- Terminal-style web interface
- Full personality system with 14,641 knowledge vectors

---

## Prerequisites

### Required Accounts
1. **Render.com account** - Sign up at https://render.com
2. **GitHub account** - For code repository
3. **Pinecone account** - Already set up with API key
4. **OpenAI account** - Already set up with API key

### Required API Keys
- `OPENAI_API_KEY` - Your OpenAI API key
- `PINECONE_API_KEY` - Your Pinecone API key (starts with `YOUR_PINECONE_API_KEY`)
- `PINECONE_ENVIRONMENT` - Set to `us-east-1`

---

## Deployment Methods

### Method 1: Deploy via Render Dashboard (Recommended)

**Step 1: Push Code to GitHub**

```bash
cd /home/ubuntu/rook-core

# Initialize git if not already done
git init
git add .
git commit -m "Initial ROOK deployment"

# Create a new repository on GitHub, then:
git remote add origin https://github.com/YOUR_USERNAME/rook-core.git
git branch -M main
git push -u origin main
```

**Step 2: Create Web Service in Render**

1. Go to https://dashboard.render.com
2. Click **"New +"** → **"Web Service"**
3. Connect your GitHub repository (`rook-core`)
4. Configure the service:

```
Name: rook-chat
Region: Oregon (US West)
Branch: main
Runtime: Python 3
Build Command: pip install --upgrade pip && pip install -r requirements.txt
Start Command: cd api && uvicorn chat_server:app --host 0.0.0.0 --port $PORT
Instance Type: Starter ($7/month)
```

**Step 3: Add Environment Variables**

In the Render dashboard, add these environment variables:

| Key | Value |
|-----|-------|
| `PYTHON_VERSION` | `3.11.0` |
| `OPENAI_API_KEY` | `your-openai-api-key` |
| `PINECONE_API_KEY` | `YOUR_PINECONE_API_KEY` |
| `PINECONE_ENVIRONMENT` | `us-east-1` |

**Step 4: Deploy**

1. Click **"Create Web Service"**
2. Render will automatically build and deploy
3. Wait 3-5 minutes for deployment to complete
4. Your ROOK chat will be live at: `https://rook-chat.onrender.com`

---

### Method 2: Deploy via render.yaml (Infrastructure as Code)

**Step 1: Push Code with render.yaml**

The `render.yaml` file is already in the repository. Just push to GitHub:

```bash
cd /home/ubuntu/rook-core
git add render.yaml
git commit -m "Add Render configuration"
git push
```

**Step 2: Create Blueprint in Render**

1. Go to https://dashboard.render.com
2. Click **"New +"** → **"Blueprint"**
3. Connect your GitHub repository
4. Render will detect `render.yaml` and configure automatically
5. Add environment variables (same as Method 1, Step 3)
6. Click **"Apply"**

---

### Method 3: Deploy via Render CLI (Advanced)

**Step 1: Install Render CLI**

```bash
npm install -g @render/cli
# or
brew install render
```

**Step 2: Login**

```bash
render login
```

**Step 3: Deploy**

```bash
cd /home/ubuntu/rook-core
render deploy
```

---

## Post-Deployment

### Verify Deployment

1. **Check Health Endpoint**
   ```bash
   curl https://rook-chat.onrender.com/health
   ```
   Should return: `{"status":"healthy","service":"ROOK Chat API"}`

2. **Test Chat Interface**
   - Open `https://rook-chat.onrender.com/` in browser
   - Should see terminal boot sequence
   - Try chatting with ROOK

3. **Test API**
   ```bash
   curl -X POST https://rook-chat.onrender.com/api/chat \
     -H "Content-Type: application/json" \
     -d '{"message": "Hello ROOK"}'
   ```

### Monitor Logs

1. Go to Render dashboard
2. Click on your `rook-chat` service
3. Click **"Logs"** tab
4. Watch for:
   - ✅ "🤖 Initializing ROOK..."
   - ✅ "✅ ROOK initialized!"
   - ✅ "Uvicorn running on..."

### Custom Domain (Optional)

1. In Render dashboard, go to your service
2. Click **"Settings"** → **"Custom Domain"**
3. Add your domain (e.g., `chat.rookai.com`)
4. Follow DNS configuration instructions
5. Render provides free SSL certificates

---

## Troubleshooting

### Build Fails

**Error:** `Could not find a version that satisfies the requirement...`

**Fix:** Update `requirements.txt` with specific versions:
```
openai==1.3.5
pinecone-client==3.0.0
fastapi==0.104.1
uvicorn[standard]==0.24.0
```

### Service Won't Start

**Error:** `Application startup failed`

**Fix:** Check environment variables are set correctly:
```bash
# In Render dashboard, verify:
- OPENAI_API_KEY is set
- PINECONE_API_KEY is set  
- PINECONE_ENVIRONMENT is set to "us-east-1"
```

### 500 Internal Server Error

**Error:** API returns 500 errors

**Fix:** Check logs for Pinecone connection errors:
```
# Common issue: Invalid Pinecone API key
# Solution: Regenerate key in Pinecone dashboard
```

### Slow Response Times

**Issue:** ROOK takes >30 seconds to respond

**Fix:** Render Starter plan has limited resources. Upgrade to:
- **Standard**: $25/month (2GB RAM)
- **Pro**: $85/month (4GB RAM)

---

## Cost Estimate

### Render Hosting
- **Starter**: $7/month (512MB RAM) - Good for testing
- **Standard**: $25/month (2GB RAM) - Recommended for production
- **Pro**: $85/month (4GB RAM) - High traffic

### External Services
- **Pinecone**: Free tier (1 index, 100K vectors) - Currently using
- **OpenAI**: Pay-as-you-go (~$0.01-0.05 per conversation)

**Total Monthly Cost:**
- Testing: ~$7-10/month
- Production: ~$25-30/month
- High Traffic: ~$85-100/month

---

## Architecture

```
User Browser
    ↓
Render Web Service (FastAPI)
    ↓
ROOK Personality Layer
    ↓
├── Pinecone (Memory & Knowledge)
│   ├── rook-memory (21 formative events)
│   ├── rook-personality-and-knowledge (35 vectors)
│   ├── rook-people-database (2,988 people)
│   ├── rook-tools (744 investigative tools)
│   └── rook-interview-database (69 interviews)
│
└── OpenAI API (GPT-4o-mini)
```

---

## Security Notes

### Environment Variables
- **Never commit API keys** to GitHub
- Use Render's environment variable system
- Rotate keys periodically

### HTTPS
- Render provides free SSL certificates
- All traffic is encrypted by default

### Rate Limiting
- Consider adding rate limiting for public deployment
- Render has built-in DDoS protection

---

## Next Steps After Deployment

### 1. Test Thoroughly
- Chat with ROOK extensively
- Test memory storage
- Verify knowledge base access

### 2. Monitor Usage
- Watch Render metrics (CPU, memory, requests)
- Monitor OpenAI API usage
- Check Pinecone query counts

### 3. Implement User Isolation
- Per-user memory spaces (see MEMORY_ARCHITECTURE_ROADMAP.md)
- User authentication
- Memory approval system

### 4. Add Features
- SEC EDGAR integration
- Fraud detection rules
- Hypothesis engine

---

## Support

### Render Support
- Documentation: https://render.com/docs
- Community: https://community.render.com
- Support: support@render.com

### ROOK Issues
- Check logs in Render dashboard
- Review ROOK_ROADMAP_UPDATED.md for known issues
- Test locally first before deploying

---

## Quick Reference

**Render Dashboard:** https://dashboard.render.com  
**Your Service:** https://rook-chat.onrender.com  
**Health Check:** https://rook-chat.onrender.com/health  
**API Endpoint:** https://rook-chat.onrender.com/api/chat  

**Environment Variables Needed:**
- `OPENAI_API_KEY`
- `PINECONE_API_KEY`
- `PINECONE_ENVIRONMENT`

**Build Command:**
```
pip install --upgrade pip && pip install -r requirements.txt
```

**Start Command:**
```
cd api && uvicorn chat_server:app --host 0.0.0.0 --port $PORT
```

---

**Status:** Ready to deploy  
**Estimated Deployment Time:** 5-10 minutes  
**Monthly Cost:** $7-25 (depending on plan)
