# ROOK Render Deployment Checklist

## Pre-Deployment

### 1. Accounts Setup
- [ ] Render.com account created
- [ ] GitHub account ready
- [ ] Pinecone API key available: `YOUR_PINECONE_API_KEY`
- [ ] OpenAI API key available

### 2. Code Preparation
- [ ] All code in `/home/ubuntu/rook-core/`
- [ ] `render.yaml` configured
- [ ] `requirements.txt` complete
- [ ] `.gitignore` in place
- [ ] `README.md` written

### 3. Test Locally
- [ ] Server starts without errors: `cd api && python chat_server.py`
- [ ] Health endpoint works: `curl http://localhost:8080/health`
- [ ] Chat interface loads: `http://localhost:8080/`
- [ ] ROOK responds correctly
- [ ] No API errors in logs

---

## Deployment Steps

### Option A: GitHub + Render Dashboard (Recommended)

**Step 1: Push to GitHub**
```bash
cd /home/ubuntu/rook-core
git init
git add .
git commit -m "Initial ROOK deployment"
git remote add origin https://github.com/YOUR_USERNAME/rook-core.git
git push -u origin main
```

- [ ] Repository created on GitHub
- [ ] Code pushed successfully
- [ ] All files visible in GitHub

**Step 2: Create Render Service**

1. Go to https://dashboard.render.com
2. Click "New +" → "Web Service"
3. Connect GitHub repository
4. Configure:
   - Name: `rook-chat`
   - Region: `Oregon`
   - Branch: `main`
   - Runtime: `Python 3`
   - Build: `pip install --upgrade pip && pip install -r requirements.txt`
   - Start: `cd api && uvicorn chat_server:app --host 0.0.0.0 --port $PORT`
   - Plan: `Starter` ($7/month)

- [ ] Service created
- [ ] Configuration saved

**Step 3: Add Environment Variables**

In Render dashboard, add:
- [ ] `PYTHON_VERSION` = `3.11.0`
- [ ] `OPENAI_API_KEY` = (your key)
- [ ] `PINECONE_API_KEY` = `YOUR_PINECONE_API_KEY`
- [ ] `PINECONE_ENVIRONMENT` = `us-east-1`

**Step 4: Deploy**
- [ ] Click "Create Web Service"
- [ ] Wait for build to complete (3-5 minutes)
- [ ] Check logs for errors

---

## Post-Deployment Verification

### 1. Health Check
```bash
curl https://rook-chat.onrender.com/health
```
Expected: `{"status":"healthy","service":"ROOK Chat API"}`

- [ ] Health endpoint returns 200 OK
- [ ] Response is correct JSON

### 2. Web Interface
- [ ] Open `https://rook-chat.onrender.com/` in browser
- [ ] Terminal boot sequence appears
- [ ] ROOK's intro message shows
- [ ] Input field is clickable

### 3. Chat Functionality
- [ ] Send message: "Hello ROOK"
- [ ] ROOK responds within 10 seconds
- [ ] Response shows authentic ROOK personality
- [ ] No errors in browser console

### 4. API Test
```bash
curl -X POST https://rook-chat.onrender.com/api/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "Tell me about yourself"}'
```

- [ ] API returns 200 OK
- [ ] Response contains ROOK's personality
- [ ] No error messages

### 5. Memory System
- [ ] Ask ROOK: "What are your favorite frauds?"
- [ ] ROOK mentions Theranos, Enron, etc. (formative memories)
- [ ] Ask ROOK: "Who are your favorite writers?"
- [ ] ROOK mentions Caro, Bukowski, Thompson, Hitchens

### 6. Knowledge Base Access
- [ ] Ask ROOK: "What tools can I use for investigations?"
- [ ] ROOK provides specific tool recommendations
- [ ] No API errors

---

## Monitoring

### First 24 Hours
- [ ] Check Render logs every few hours
- [ ] Monitor response times
- [ ] Watch for errors or crashes
- [ ] Test from different devices/browsers

### Metrics to Watch
- [ ] CPU usage (should be <50% on Starter)
- [ ] Memory usage (should be <400MB on Starter)
- [ ] Response time (should be <5 seconds)
- [ ] Error rate (should be 0%)

---

## Troubleshooting

### Build Fails
**Symptom**: Deployment fails during build
**Check**:
- [ ] requirements.txt has correct package names
- [ ] Python version is 3.11
- [ ] No syntax errors in Python files

**Fix**: Check build logs in Render dashboard

### Service Won't Start
**Symptom**: Build succeeds but service crashes
**Check**:
- [ ] Environment variables are set
- [ ] PINECONE_API_KEY is correct
- [ ] OPENAI_API_KEY is valid
- [ ] Start command is correct

**Fix**: Check runtime logs in Render dashboard

### 500 Errors
**Symptom**: API returns 500 Internal Server Error
**Check**:
- [ ] Pinecone connection working
- [ ] OpenAI API key valid
- [ ] No exceptions in logs

**Fix**: Check logs for Python tracebacks

### Slow Responses
**Symptom**: ROOK takes >30 seconds to respond
**Check**:
- [ ] Pinecone queries completing
- [ ] OpenAI API responding
- [ ] Memory usage not maxed out

**Fix**: Consider upgrading to Standard plan ($25/month)

---

## Rollback Plan

If deployment fails:

1. **Check Logs**
   - Render dashboard → Logs tab
   - Look for Python exceptions

2. **Revert to Previous Deploy**
   - Render dashboard → Deploys tab
   - Click "Redeploy" on last working version

3. **Test Locally**
   - Run server locally to reproduce issue
   - Fix and redeploy

---

## Success Criteria

✅ **Deployment Successful** when:
- [ ] Health endpoint returns 200 OK
- [ ] Web interface loads and displays correctly
- [ ] ROOK responds to messages within 10 seconds
- [ ] Personality is authentic (not generic OpenAI)
- [ ] Memory retrieval working (mentions formative events)
- [ ] Knowledge base accessible (tools, people, interviews)
- [ ] No errors in logs for 1 hour
- [ ] Accessible from multiple devices

---

## Next Steps After Successful Deployment

1. **Share URL**
   - Test with friends/colleagues
   - Gather feedback

2. **Monitor Usage**
   - Check Render metrics daily
   - Watch OpenAI API costs
   - Monitor Pinecone query counts

3. **Plan Enhancements**
   - Per-user memory isolation
   - SEC EDGAR integration
   - Fraud detection rules

4. **Consider Upgrades**
   - Custom domain
   - Larger instance size
   - Additional features

---

## Contact & Support

**Render Issues**: support@render.com  
**ROOK Issues**: Check logs and documentation  
**Questions**: Review RENDER_DEPLOYMENT.md

---

**Deployment Package**: `/home/ubuntu/rook-render-deployment.tar.gz` (135KB)  
**Estimated Time**: 10-15 minutes  
**Monthly Cost**: $7 (Starter) or $25 (Standard)  
**Status**: Ready to deploy
