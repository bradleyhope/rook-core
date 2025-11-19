# ROOK Railway Deployment Guide

## ✅ Completed Steps

1. **Railway Project Created**: `rook-ai-journalist`
   - Project URL: https://railway.com/project/cf512c62-ad6d-448c-b4aa-f584befa7afe
   - Project ID: `cf512c62-ad6d-448c-b4aa-f584befa7afe`

2. **PostgreSQL Database Added**
   - Service ID: `9d31e17c-1e01-4c09-88ff-c83c47baa519`
   - Automatically provisioned with Railway

3. **ROOK API Service Created**
   - Service ID: `abb38361-e86a-4820-982c-4ce82ec93a73`
   - Service Name: `rook-api`

4. **Deployment Files Prepared**
   - ✅ `Dockerfile` - Container configuration
   - ✅ `requirements.txt` - Python dependencies
   - ✅ `railway.json` - Railway deployment configuration
   - ✅ `.railwayignore` - Files to exclude from deployment
   - ✅ `api/main.py` - FastAPI application

## 🔧 Required: Set Environment Variables

The Railway GraphQL API timed out when setting environment variables. Please set them manually in the Railway dashboard:

### Steps to Set Environment Variables:

1. Go to: https://railway.com/project/cf512c62-ad6d-448c-b4aa-f584befa7afe
2. Click on the **rook-api** service
3. Go to the **Variables** tab
4. Add the following environment variables:

```
OPENAI_API_KEY=YOUR_OPENAI_API_KEY

PINECONE_API_KEY=YOUR_PINECONE_API_KEY

PINECONE_ENVIRONMENT=us-east-1

PORT=8000
```

### PostgreSQL Connection (Automatic):
Railway will automatically inject the `DATABASE_URL` variable when you reference the Postgres service.

## 🚀 Deploy Options

### Option 1: Deploy via Railway CLI (Recommended)

```bash
cd /home/ubuntu/rook-core
export RAILWAY_API_TOKEN="c94983fb-fa4d-49af-8760-6238d530b510"

# Link to the rook-api service
railway link cf512c62-ad6d-448c-b4aa-f584befa7afe

# Deploy
railway up --service abb38361-e86a-4820-982c-4ce82ec93a73
```

### Option 2: Deploy via GitHub

1. Create a GitHub repository for ROOK
2. Push the code to GitHub:
   ```bash
   cd /home/ubuntu/rook-core
   git init
   git add .
   git commit -m "Initial ROOK deployment"
   git remote add origin <your-github-repo-url>
   git push -u origin main
   ```
3. In Railway dashboard, connect the GitHub repository to the `rook-api` service
4. Railway will automatically deploy on every push

### Option 3: Manual Upload via Railway Dashboard

1. Go to the rook-api service in Railway dashboard
2. Click on **Settings** → **Source**
3. Upload the `/home/ubuntu/rook-core` directory as a ZIP file

## 📋 Project Structure

```
/home/ubuntu/rook-core/
├── api/
│   └── main.py              # FastAPI application
├── src/
│   ├── rook_enhanced.py     # Main ROOK system
│   ├── personality/         # Personality layer (Pinecone)
│   ├── safety/              # Safety & trust layer
│   ├── routing/             # Query routing
│   └── ...
├── Dockerfile               # Container configuration
├── requirements.txt         # Python dependencies
├── railway.json             # Railway configuration
└── .railwayignore          # Deployment exclusions
```

## 🔍 Verification Steps

After deployment:

1. **Check Service Status**
   - Go to Railway dashboard
   - Verify `rook-api` service is running
   - Check deployment logs for errors

2. **Test Health Endpoint**
   ```bash
   curl https://<your-railway-domain>/health
   ```

3. **Test Investigation Endpoint**
   ```bash
   curl -X POST https://<your-railway-domain>/investigate \
     -H "Content-Type: application/json" \
     -d '{"query": "What patterns should I look for in financial fraud?"}'
   ```

## 💰 Cost Estimate

- **Railway Hobby Plan**: $5/month
- **PostgreSQL**: Included in Hobby plan
- **ROOK API Service**: ~$5-10/month (depending on usage)
- **Pinecone Free Tier**: $0 (up to 1 index, 100K vectors)
- **Total**: ~$10-15/month for launch

## 🔐 Security Notes

1. **Environment Variables**: All sensitive keys are stored as Railway environment variables (encrypted)
2. **OpenAI API**: Uses explicit base_url to bypass proxies
3. **Database**: PostgreSQL with automatic backups
4. **HTTPS**: Automatically provisioned by Railway

## 📚 API Documentation

Once deployed, visit:
- Health Check: `https://<your-domain>/health`
- API Docs: `https://<your-domain>/docs` (FastAPI auto-generated)
- OpenAPI Schema: `https://<your-domain>/openapi.json`

## 🐛 Troubleshooting

### Service Won't Start
- Check deployment logs in Railway dashboard
- Verify all environment variables are set
- Ensure Pinecone index exists: `rook-personality-and-knowledge`

### OpenAI API Errors
- Verify `OPENAI_API_KEY` is set correctly
- Check that `base_url='https://api.openai.com/v1'` is in code (already configured)

### Pinecone Connection Errors
- Verify `PINECONE_API_KEY` is set
- Ensure index name matches: `rook-personality-and-knowledge`
- Check Pinecone dashboard for index status

### Database Connection Errors
- Verify Postgres service is running
- Check that `DATABASE_URL` is automatically injected
- Review Railway service connections

## 🎯 Next Steps (Phase 4)

1. **SEC EDGAR Integration**
   - Build document ingestion pipeline
   - Connect to SEC EDGAR API
   - Store documents in PostgreSQL

2. **Fraud Detection Rules**
   - Implement 10 fraud pattern detection rules
   - Integrate with ROOK's investigation engine

3. **Sleep Consolidation**
   - Build memory consolidation system
   - Implement experience-based learning

4. **Scaling**
   - Monitor usage and costs
   - Migrate to AWS when needed
   - Implement caching layer

## 📞 Support

- Railway Documentation: https://docs.railway.com
- Railway Discord: https://discord.gg/railway
- ROOK GitHub Issues: (create repository)

---

**Deployment Status**: ⚠️ Awaiting environment variable configuration and code deployment
