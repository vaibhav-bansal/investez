# Quick Deploy Guide - InvestEz

## What You're Deploying

- **Marketing site** at `investez.vercel.app`
- **Dashboard** at `investez.vercel.app/dashboard`
- **API backend** at Railway

---

## Step-by-Step

### 1. Deploy Marketing Site

Go to https://vercel.com/new

- **Import**: Select your GitHub repo `vaibhav-bansal/investez`
- **Root Directory**: `marketing`
- **Framework**: Vite (auto-detected)
- **Build Command**: Leave default or set to `npm run build`
- **Install Command**: `npm install --legacy-peer-deps`

Click **Deploy**.

You'll get: `investez.vercel.app` ✅

---

### 2. Deploy Dashboard

Go to https://vercel.com/new again (NEW project)

- **Import**: Same repo `vaibhav-bansal/investez`
- **Root Directory**: `frontend`
- **Framework**: Vite
- **Build Command**: `npm run build`

Click **Deploy**.

You'll get: `investez-dashboard-xxx.vercel.app` (temporary URL)

---

### 3. Connect Dashboard to Marketing Domain

In the **marketing project** on Vercel:

1. Go to **Settings** → **Rewrites and Redirects**
2. Click **Add Redirect/Rewrite**
3. Select **Rewrite**
4. Fill in:
   - **Source**: `/dashboard/:path*`
   - **Destination**: `https://investez-dashboard-xxx.vercel.app/:path*`
     (Use the actual URL from step 2)
5. Save

Now `investez.vercel.app/dashboard` works! ✅

---

### 4. Deploy Backend to Railway

Install Railway CLI:
```bash
npm install -g @railway/cli
```

Login and deploy:
```bash
railway login
cd api
railway init
railway up
```

You'll get a Railway URL like: `xxx.up.railway.app`

---

### 5. Connect Dashboard to Backend

#### A. Update frontend/vercel.json

Replace `YOUR_RAILWAY_URL_HERE` with your actual Railway URL:
```json
{
  "rewrites": [
    {
      "source": "/api/:path*",
      "destination": "https://YOUR_ACTUAL_RAILWAY_URL.up.railway.app/api/:path*"
    }
  ]
}
```

#### B. Update in Vercel Dashboard

Go to **Dashboard project** → **Settings** → **Environment Variables**

Add:
- **Name**: `VITE_API_URL`
- **Value**: `https://YOUR_ACTUAL_RAILWAY_URL.up.railway.app`

#### C. Redeploy Dashboard

In the dashboard project, click **Deployments** → **...** → **Redeploy**

---

## Done!

Test your sites:
- Marketing: https://investez.vercel.app
- Dashboard: https://investez.vercel.app/dashboard
- API: https://xxx.up.railway.app/api/health (if you have a health endpoint)

---

## If You Get Errors

### "Build failed" on Vercel

In project settings, set:
- **Install Command**: `npm install --legacy-peer-deps`

### "API calls fail" from dashboard

1. Check Railway is running
2. Add CORS in `api/config.py`:
```python
CORS_ORIGINS = [
    'https://investez.vercel.app',
    'https://investez-dashboard-xxx.vercel.app'  # Your actual dashboard URL
]
```
3. Redeploy Railway: `railway up`

### "/dashboard shows 404"

Check the rewrite rule in marketing project settings. Make sure:
- Source is `/dashboard/:path*`
- Destination has `https://` and correct URL

---

## Quick Reference

| Component | Service | How to Deploy | URL |
|-----------|---------|---------------|-----|
| Marketing | Vercel | Root: `marketing/` | investez.vercel.app |
| Dashboard | Vercel | Root: `frontend/` | investez.vercel.app/dashboard |
| Backend | Railway | `railway up` from `api/` | xxx.up.railway.app |

All free tier! 🎉
