# Deployment Guide - DeutschSpectrum Backend

This guide will help you deploy the DeutschSpectrum backend to Railway for free.

## Prerequisites

- GitHub account
- Railway account (sign up at https://railway.app with GitHub)

## Step-by-Step Deployment

### 1. Push Code to GitHub

```bash
cd /Users/amrmustafa/projects/langlearn
git init
git add .
git commit -m "Initial commit - DeutschSpectrum backend"
git branch -M main
git remote add origin YOUR_GITHUB_REPO_URL
git push -u origin main
```

### 2. Deploy to Railway

1. **Go to Railway:** https://railway.app
2. **Sign in** with your GitHub account
3. **Create New Project** → **Deploy from GitHub repo**
4. **Select your repository:** `langlearn` or whatever you named it
5. **Select root directory:** Change to `/backend` (important!)
6. **Railway will automatically:**
   - Detect it's a Python project
   - Install dependencies from requirements.txt
   - Download the spaCy model
   - Start the server

### 3. Configure Environment (if needed)

Railway should work out of the box, but if you need to set environment variables:

1. Go to your project in Railway
2. Click **Variables** tab
3. Add any needed variables (currently none required)

### 4. Get Your Production URL

1. In Railway, go to your service
2. Click **Settings** tab
3. Scroll to **Networking** section
4. Click **Generate Domain**
5. Copy the URL (e.g., `https://your-app.railway.app`)

### 5. Update Extension

Update the extension's default backend URL:

1. Open `extension/popup/popup.html`
2. Find the backend URL input (line ~110):
   ```html
   <input type="text" id="backend-url" value="http://localhost:8000" ...>
   ```
3. Change to your Railway URL:
   ```html
   <input type="text" id="backend-url" value="https://your-app.railway.app" ...>
   ```

### 6. Test Your Deployment

Test the health endpoint:
```bash
curl https://your-app.railway.app/api/v1/health
```

Expected response:
```json
{
  "status": "healthy",
  "model_loaded": true
}
```

## Free Tier Limits

Railway's free tier includes:
- $5 of usage per month (usually ~500 hours)
- Automatic sleep after 15 minutes of inactivity
- First request after sleep takes ~30 seconds (cold start for model loading)

**This is perfect for:**
- Personal use
- Testing
- Small user base (< 100 active users)

## Scaling Beyond Free Tier

If you exceed the free tier:
- Railway charges $5/month for 500 more hours
- Alternative: Deploy to Render.com (similar free tier)
- Alternative: Deploy to Fly.io (also has free tier)

## Monitoring

View logs in Railway:
1. Click on your service
2. Click **Logs** tab
3. Monitor requests and errors in real-time

## Troubleshooting

### Model Download Fails
If spaCy model download fails during deployment:
1. Check Railway logs
2. Increase healthcheck timeout in railway.json
3. Redeploy

### Cold Starts Too Slow
The first request after sleep takes time because:
1. Container wakes up (~5 seconds)
2. Python starts (~5 seconds)
3. spaCy model loads (~20 seconds)

To prevent sleep:
- Upgrade to Railway Pro ($5/month - no sleep)
- Or set up a free cron job to ping the health endpoint every 10 minutes

### CORS Errors
CORS is already configured to allow all origins (`allow_origins=["*"]`), so this shouldn't be an issue.

## Alternative: Deploy to Render

If you prefer Render:

1. Go to https://render.com
2. Sign up with GitHub
3. **New** → **Web Service**
4. Connect your GitHub repo
5. **Root Directory:** `backend`
6. **Build Command:** `pip install -r requirements.txt && python -m spacy download de_core_news_lg`
7. **Start Command:** `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
8. **Instance Type:** Free
9. Click **Create Web Service**

Render's free tier:
- Automatic HTTPS
- Custom domains
- Spins down after 15 min inactivity
- Slower cold starts (~1 minute)

## Support

If you run into issues, check:
- Railway documentation: https://docs.railway.app
- FastAPI deployment guide: https://fastapi.tiangolo.com/deployment/
- spaCy installation: https://spacy.io/usage
