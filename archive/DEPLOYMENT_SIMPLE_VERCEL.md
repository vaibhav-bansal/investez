# InvestEz Deployment - Simple Strategy

## Architecture

```
investez.vercel.app/          → Marketing site
investez.vercel.app/dashboard → Dashboard app (via rewrite)

api.investez.app              → Flask backend (Railway)
```

## Option 1: Two Vercel Projects (Recommended - Easiest)

### Step 1: Deploy Marketing (Main Domain)

**Via Vercel Dashboard:**
1. Go to https://vercel.com/new
2. Import: `vaibhav-bansal/investez`
3. **Project Name**: `investez-marketing`
4. **Root Directory**: `marketing`
5. **Framework**: Vite
6. **Build Command**: `npm run build`
7. **Install Command**: `npm install --legacy-peer-deps`
8. Deploy

This gives you: `investez.vercel.app`

### Step 2: Deploy Dashboard (Separate Project)

**Via Vercel Dashboard:**
1. Create NEW project (don't add to existing)
2. Import same repo: `vaibhav-bansal/investez`
3. **Project Name**: `investez-dashboard`
4. **Root Directory**: `frontend`
5. **Framework**: Vite
6. **Build Command**: `npm run build`
7. Deploy

This gives you: `investez-dashboard.vercel.app` (temporary)

### Step 3: Add Rewrite to Marketing Project

In the **marketing project** on Vercel:

1. Go to Settings → Rewrites
2. Add rewrite:
   - **Source**: `/dashboard/:path*`
   - **Destination**: `https://investez-dashboard.vercel.app/:path*`

Now:
- `investez.vercel.app` → Marketing
- `investez.vercel.app/dashboard` → Dashboard (proxied)

---

## Option 2: Vercel CLI (Same Result)

### Deploy Marketing

```bash
cd marketing
npm install -g vercel
vercel login
vercel --prod
```

### Deploy Dashboard

```bash
cd frontend
vercel --prod
```

Then add the rewrite rule in Vercel dashboard as above.

---

## Option 3: vercel.json Configuration (Most Control)

Create `vercel.json` in ROOT of repository:

```json
{
  "version": 2,
  "builds": [
    {
      "src": "marketing/package.json",
      "use": "@vercel/static-build",
      "config": {
        "distDir": "marketing/dist"
      }
    }
  ],
  "rewrites": [
    {
      "source": "/dashboard/:path*",
      "destination": "https://YOUR-DASHBOARD-VERCEL-URL.vercel.app/:path*"
    },
    {
      "source": "/(.*)",
      "destination": "/marketing/dist/$1"
    }
  ]
}
```

---

## Backend Deployment (Railway)

### Quick Start

```bash
# Install Railway CLI
npm install -g @railway/cli

# Login
railway login

# Deploy from api folder
cd api
railway init
railway up
```

### Configuration

Create `api/railway.json`:

```json
{
  "$schema": "https://railway.app/railway.schema.json",
  "build": {
    "builder": "nixpacks",
    "buildCommand": "pip install -r requirements.txt"
  },
  "deploy": {
    "startCommand": "gunicorn --bind 0.0.0.0:$PORT api:app",
    "restartPolicyType": "ON_FAILURE"
  }
}
```

Add to `requirements.txt`:
```
gunicorn==21.2.0
```

### Add Database Volume

In Railway dashboard:
1. Add Volume
2. Mount at: `/app/data`
3. Set env var: `DATABASE_PATH=/app/data/kite_db.sqlite`

---

## What You Actually Need to Do

### For Marketing + Dashboard on Same Domain:

**Simplest Approach:**

1. **Deploy Marketing**:
   ```bash
   cd marketing
   vercel --prod
   ```
   Note the URL: `investez.vercel.app`

2. **Deploy Dashboard**:
   ```bash
   cd frontend
   vercel --prod
   ```
   Note the URL: `investez-dashboard-xxx.vercel.app`

3. **Add Rewrite** in Vercel dashboard (Marketing project):
   - Settings → Rewrites and Redirects
   - Source: `/dashboard/:path*`
   - Destination: `https://investez-dashboard-xxx.vercel.app/:path*`

4. **Deploy Backend** to Railway:
   ```bash
   cd api
   railway up
   ```
   Note the URL: `xxx.up.railway.app`

5. **Update Dashboard** with API URL:
   - In frontend project on Vercel
   - Settings → Environment Variables
   - Add: `VITE_API_URL=https://xxx.up.railway.app`
   - Redeploy: `vercel --prod`

Done! Now:
- `investez.vercel.app` → Marketing
- `investez.vercel.app/dashboard` → Dashboard
- API at Railway

---

## Common Errors & Fixes

### Error: "Build failed in marketing/"
**Fix**:
```bash
cd marketing
npm install --legacy-peer-deps
npm run build  # Test locally first
```

### Error: "Module not found" on Vercel
**Fix**: Set install command to `npm install --legacy-peer-deps` in Vercel dashboard

### Error: "/dashboard redirects to wrong place"
**Fix**: Check rewrite destination URL is correct (must include https://)

### Error: "API calls fail from dashboard"
**Fix**:
1. Add CORS origins in Flask `api/config.py`:
   ```python
   CORS_ORIGINS = [
       'https://investez.vercel.app',
       'https://investez-dashboard-xxx.vercel.app'
   ]
   ```
2. Redeploy Railway: `railway up`

---

## Summary

**2 Vercel Projects + 1 Railway Service**

| What | Where | URL |
|------|-------|-----|
| Marketing | Vercel Project 1 | investez.vercel.app |
| Dashboard | Vercel Project 2 (proxied via rewrite) | investez.vercel.app/dashboard |
| Backend | Railway | xxx.up.railway.app |

**Cost**: Free (both Vercel hobby plans + Railway free tier)
