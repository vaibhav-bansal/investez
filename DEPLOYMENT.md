# InvestEz Deployment Guide

Complete guide for deploying all three parts of InvestEz.

## Architecture Overview

```
┌─────────────────────────────────────┐
│  investez.vercel.app (Marketing)    │
│  - Static React + Vite site         │
│  - No backend needed                │
└─────────────────────────────────────┘

┌─────────────────────────────────────┐
│  app.investez.vercel.app (Dashboard)│
│  - React + Vite frontend            │
│  - Proxies API calls to Railway     │
└──────────────┬──────────────────────┘
               │ API calls
               ↓
┌─────────────────────────────────────┐
│  api.investez.app (Backend)         │
│  - Flask + SQLite on Railway        │
│  - Persistent storage               │
└─────────────────────────────────────┘
```

---

## Part 1: Marketing Website (Vercel)

### Deploy to Vercel

**Option 1: Vercel CLI (Recommended)**
```bash
cd marketing
npm install -g vercel
vercel login
vercel --prod
```

**Option 2: Vercel Dashboard**
1. Go to https://vercel.com/new
2. Import repository: `vaibhav-bansal/investez`
3. **Root Directory**: `marketing`
4. **Framework Preset**: Vite
5. **Build Command**: `npm run build`
6. **Output Directory**: `dist`
7. **Install Command**: `npm install --legacy-peer-deps`

### Configuration

The `marketing/vercel.json` is already configured with:
- SPA routing (all routes → index.html)
- Security headers
- CORS for `.well-known/` files (AI discovery)

### Domain

- **Production**: `investez.vercel.app`
- **Custom domain** (optional): Add in Vercel dashboard → Domains

### Environment Variables

No environment variables needed for marketing site.

---

## Part 2: Dashboard Frontend (Vercel)

### Deploy to Vercel

**Option 1: Vercel CLI**
```bash
cd frontend
vercel login
vercel --prod
```

**Option 2: Vercel Dashboard**
1. Create **NEW PROJECT** (separate from marketing)
2. Import same repository: `vaibhav-bansal/investez`
3. **Root Directory**: `frontend`
4. **Framework Preset**: Vite
5. **Build Command**: `npm run build`
6. **Output Directory**: `dist`

### Configuration

Update `frontend/vercel.json` after deploying backend:
```json
{
  "rewrites": [
    {
      "source": "/api/:path*",
      "destination": "https://your-api.up.railway.app/api/:path*"
    }
  ]
}
```

### Domain

- **Suggested**: `app.investez.vercel.app` or `dashboard.investez.vercel.app`
- Add as subdomain in Vercel dashboard

### Environment Variables

Set in Vercel dashboard → Settings → Environment Variables:
```
VITE_API_URL=https://your-api.up.railway.app
```

---

## Part 3: Flask API Backend (Railway)

### Why Railway (Not Vercel)?

Vercel serverless functions have:
- ❌ Ephemeral filesystem (SQLite resets on each deploy)
- ❌ Limited execution time (10s for hobby tier)
- ❌ No persistent storage

Railway provides:
- ✅ Persistent disk volumes
- ✅ Long-running processes
- ✅ PostgreSQL/MySQL options
- ✅ Free tier with $5 credit/month

---

## Deploy Backend to Railway

### Step 1: Create Railway Project

```bash
# Install Railway CLI
npm install -g @railway/cli

# Login to Railway
railway login

# Navigate to api folder
cd api

# Initialize Railway project
railway init

# Link to new project
railway link
```

### Step 2: Configure Railway

Create `railway.toml` in `api/` folder:
```toml
[build]
builder = "NIXPACKS"
buildCommand = "pip install -r requirements.txt"

[deploy]
startCommand = "gunicorn --bind 0.0.0.0:$PORT api:app"
restartPolicyType = "ON_FAILURE"
restartPolicyMaxRetries = 10
```

### Step 3: Add Gunicorn

Update `api/requirements.txt`:
```txt
Flask==3.0.0
Flask-CORS==4.0.0
python-dotenv==1.0.0
requests==2.31.0
gunicorn==21.2.0
```

### Step 4: Update Flask Configuration

Update `api/config.py`:
```python
import os

class Config:
    # Database
    DATABASE_PATH = os.getenv('DATABASE_PATH', './kite_db.sqlite')

    # Flask
    SECRET_KEY = os.getenv('SECRET_KEY', 'your-secret-key-here')

    # CORS - Allow frontend domains
    CORS_ORIGINS = [
        'https://app.investez.vercel.app',
        'https://investez.vercel.app',
        'http://localhost:5173',
        'http://localhost:5174'
    ]

    # Kite API
    KITE_API_KEY = os.getenv('KITE_API_KEY')
    KITE_API_SECRET = os.getenv('KITE_API_SECRET')
    KITE_ACCESS_TOKEN = os.getenv('KITE_ACCESS_TOKEN')
```

### Step 5: Add Volume for Database

In Railway dashboard:
1. Go to your project
2. Click "Add Volume"
3. **Mount Path**: `/app/data`
4. **Size**: 1GB (free tier)

Update `config.py`:
```python
DATABASE_PATH = os.getenv('DATABASE_PATH', '/app/data/kite_db.sqlite')
```

### Step 6: Set Environment Variables

In Railway dashboard → Variables:
```
PORT=8000
DATABASE_PATH=/app/data/kite_db.sqlite
SECRET_KEY=generate-a-secure-random-key
KITE_API_KEY=your_kite_api_key
KITE_API_SECRET=your_kite_api_secret
KITE_ACCESS_TOKEN=your_kite_access_token
```

### Step 7: Deploy

```bash
railway up
```

Or push to GitHub and enable auto-deploy in Railway.

### Step 8: Get Public URL

Railway provides: `https://your-project.up.railway.app`

Or add custom domain: `api.investez.app`

---

## Update Frontend with Backend URL

After Railway deployment:

1. Get Railway URL: `https://your-api.up.railway.app`

2. Update `frontend/vercel.json`:
```json
{
  "rewrites": [
    {
      "source": "/api/:path*",
      "destination": "https://your-api.up.railway.app/api/:path*"
    }
  ]
}
```

3. Update environment variable in Vercel:
```
VITE_API_URL=https://your-api.up.railway.app
```

4. Redeploy frontend: `vercel --prod`

---

## Summary: Three Separate Deployments

| Component | Service | Domain | Root Directory |
|-----------|---------|--------|----------------|
| Marketing | Vercel | investez.vercel.app | `marketing/` |
| Dashboard | Vercel | app.investez.vercel.app | `frontend/` |
| Backend | Railway | api.investez.app | `api/` |

---

## Common Vercel Errors & Fixes

### Error: "Module not found"
**Fix**: Add `installCommand` to vercel.json:
```json
{
  "installCommand": "npm install --legacy-peer-deps"
}
```

### Error: "Build failed"
**Fix**: Check that root directory is set correctly in Vercel dashboard

### Error: "404 on refresh"
**Fix**: Ensure rewrites are configured in vercel.json:
```json
{
  "rewrites": [
    { "source": "/(.*)", "destination": "/index.html" }
  ]
}
```

### Error: "API calls fail with CORS"
**Fix**: Update Flask CORS configuration in `api/config.py` to include Vercel domains

---

## Post-Deployment Checklist

### Marketing Site
- [ ] Site loads at `investez.vercel.app`
- [ ] All sections visible and scrollable
- [ ] SEO files accessible:
  - [ ] `/robots.txt`
  - [ ] `/sitemap.xml`
  - [ ] `/.well-known/ai-plugin.json`

### Dashboard
- [ ] Site loads at `app.investez.vercel.app`
- [ ] API calls work (check browser console)
- [ ] Portfolio data displays correctly

### Backend API
- [ ] Railway service is running
- [ ] Database persists after restart
- [ ] API endpoints respond:
  - [ ] `/api/auth/status`
  - [ ] `/api/portfolio/`
- [ ] CORS allows frontend domains

---

## Local Development vs Production

### Local Development
```bash
# Marketing
cd marketing && npm run dev  # http://localhost:5173

# Dashboard
cd frontend && npm run dev   # http://localhost:5174

# Backend
cd api && python api.py      # http://localhost:5000
```

### Production URLs
```
Marketing:  https://investez.vercel.app
Dashboard:  https://app.investez.vercel.app
Backend:    https://your-api.up.railway.app
```

---

## Cost Estimate

| Service | Tier | Cost |
|---------|------|------|
| Vercel (Marketing) | Hobby | Free |
| Vercel (Dashboard) | Hobby | Free |
| Railway (Backend) | Free | $0 (with $5 credit) |
| **Total** | | **$0/month** |

Paid tiers if scaling:
- Vercel Pro: $20/month per project
- Railway: ~$5-10/month for small API

---

## Need Help?

Common issues:
1. **CORS errors**: Check Flask CORS configuration
2. **API 404**: Verify rewrites in frontend/vercel.json
3. **Database resets**: Ensure Railway volume is mounted
4. **Build fails**: Check root directory in Vercel settings

For deployment issues, check:
- Vercel: https://vercel.com/docs
- Railway: https://docs.railway.app
