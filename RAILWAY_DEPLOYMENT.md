# InvestEz Railway Deployment Guide

Complete guide for deploying all three parts of InvestEz on Railway.

## Architecture Overview

```
┌─────────────────────────────────────┐
│  Marketing Website (Railway)        │
│  - Static React + Vite site         │
│  - No backend needed                │
│  URL: investez-marketing.up.railway.app
└─────────────────────────────────────┘

┌─────────────────────────────────────┐
│  Dashboard Frontend (Railway)       │
│  - React + Vite frontend            │
│  - Connects to Backend API          │
│  URL: investez-dashboard.up.railway.app
└──────────────┬──────────────────────┘
               │ API calls
               ↓
┌─────────────────────────────────────┐
│  Backend API (Railway)              │
│  - Flask + SQLite                   │
│  - Persistent volume storage        │
│  URL: investez-api.up.railway.app
└─────────────────────────────────────┘
```

## Why Railway for Everything?

- ✅ **Single Platform**: One dashboard for all services
- ✅ **Persistent Storage**: Volume mounting for SQLite database
- ✅ **Easy Monorepo**: Deploy from one Git repository
- ✅ **Automatic HTTPS**: SSL certificates included
- ✅ **Free Tier**: $5 credit/month covers light usage
- ✅ **Simple Environment Variables**: Shared across services
- ✅ **Auto-Deploy**: Push to Git → automatic deployment

---

## Prerequisites

1. Railway account: [railway.app](https://railway.app)
2. Railway CLI installed:
   ```bash
   npm install -g @railway/cli
   ```
3. Git repository with your code

---

## Step-by-Step Deployment

### Step 1: Install Railway CLI & Login

```bash
npm install -g @railway/cli
railway login
```

### Step 2: Create Railway Project

```bash
# From your project root
railway init

# Name your project: investez
# This creates a new Railway project
```

### Step 3: Deploy Backend API

The backend needs to be deployed first so we can get its URL for the frontend.

```bash
# Navigate to API directory
cd api

# Create new service
railway up

# Railway will detect railway.toml and deploy
```

**Configure Backend Service:**

1. Go to Railway dashboard → Your Project
2. Click on the API service
3. Go to **Variables** tab and add:
   ```
   PORT=5000
   SECRET_KEY=<generate-random-32-char-string>
   DATABASE_PATH=/app/data/kite_db.sqlite
   KITE_API_KEY=<your-kite-api-key>
   KITE_API_SECRET=<your-kite-api-secret>
   KITE_ACCESS_TOKEN=<your-access-token>
   ```

4. Go to **Settings** → **Volumes**
5. Click **New Volume**:
   - Mount Path: `/app/data`
   - Size: 1GB

6. Go to **Settings** → **Networking**
7. Click **Generate Domain** to get public URL
8. Copy the URL (e.g., `https://investez-api.up.railway.app`)

### Step 4: Deploy Dashboard Frontend

```bash
# Navigate to frontend directory
cd ../frontend

# Deploy to Railway
railway up
```

**Configure Dashboard Service:**

1. In Railway dashboard → Dashboard service
2. Go to **Variables** tab and add:
   ```
   VITE_API_URL=https://investez-api.up.railway.app/api
   ```
   (Replace with your actual API URL from Step 3)

3. Also add to API service variables:
   ```
   DASHBOARD_URL=https://investez-dashboard.up.railway.app
   ```
   (Use the URL Railway generates for your dashboard)

4. Go to **Settings** → **Networking**
5. Click **Generate Domain**

### Step 5: Deploy Marketing Website

```bash
# Navigate to marketing directory
cd ../marketing

# Deploy to Railway
railway up
```

**Configure Marketing Service:**

1. In Railway dashboard → Marketing service
2. Go to **Settings** → **Networking**
3. Click **Generate Domain**
4. Copy the URL

5. Add to API service variables:
   ```
   MARKETING_URL=https://investez-marketing.up.railway.app
   ```

### Step 6: Verify Deployment

Test each service:

1. **Marketing Site**: Visit your marketing URL
   - Should see landing page with all sections

2. **Dashboard**: Visit your dashboard URL
   - Should load without errors
   - Check browser console for API connection

3. **Backend API**: Test health endpoint
   ```bash
   curl https://your-api-url.up.railway.app/api/health
   # Should return: {"status": "ok"}
   ```

---

## Project Structure

Your Railway project should have **3 services**:

```
InvestEz (Project)
├── investez-api (Service)
│   ├── Root Directory: /api
│   ├── railway.toml
│   └── Volume: /app/data
├── investez-dashboard (Service)
│   ├── Root Directory: /frontend
│   └── railway.toml
└── investez-marketing (Service)
    ├── Root Directory: /marketing
    └── railway.toml
```

---

## Environment Variables Reference

### Backend API (`api/`)
```bash
PORT=5000
SECRET_KEY=your-secret-key-generate-random-32-chars
DATABASE_PATH=/app/data/kite_db.sqlite
DASHBOARD_URL=https://investez-dashboard.up.railway.app
MARKETING_URL=https://investez-marketing.up.railway.app
KITE_API_KEY=your_kite_api_key
KITE_API_SECRET=your_kite_api_secret
KITE_ACCESS_TOKEN=your_access_token
KITE_TOKEN_EXPIRY=
```

### Dashboard Frontend (`frontend/`)
```bash
VITE_API_URL=https://investez-api.up.railway.app/api
NODE_ENV=production
```

### Marketing Website (`marketing/`)
```bash
NODE_ENV=production
```

---

## Automatic Deployments

Railway can auto-deploy on Git push:

1. Go to Railway dashboard → Service → **Settings**
2. Connect your GitHub repository
3. Set **Root Directory** for each service:
   - API: `api`
   - Dashboard: `frontend`
   - Marketing: `marketing`
4. Enable **Auto Deploy** on main branch

Now every `git push` triggers automatic deployment!

---

## Custom Domains (Optional)

Add custom domains for each service:

1. Go to service → **Settings** → **Networking**
2. Click **Custom Domain**
3. Add your domain:
   - Marketing: `investez.com`
   - Dashboard: `app.investez.com`
   - API: `api.investez.com`
4. Update DNS records as shown by Railway
5. Update environment variables with new URLs

---

## Local Development

For local development, use proxy (no env vars needed):

```bash
# Terminal 1: Backend
cd api
flask --app app run --port 5000 --debug

# Terminal 2: Dashboard
cd frontend
npm run dev

# Terminal 3: Marketing
cd marketing
npm run dev
```

The Vite dev server will proxy `/api/*` requests to `http://localhost:5000`.

---

## Monitoring & Logs

View logs in Railway dashboard:

1. Go to your project
2. Click on a service
3. Click **Logs** tab
4. See real-time logs and errors

---

## Cost Breakdown

Railway Free Tier:
- **$5 credit/month** included
- **Usage**: ~$0.01-0.02/hour per service
- **Estimate**: 3 services = ~$15-30/month
- **First month**: Free with credit
- **After credit**: ~$10-25/month for all services

To reduce costs:
- Use Railway's sleep feature for non-production environments
- Monitor usage in Railway dashboard
- Optimize API to reduce resource usage

---

## Troubleshooting

### API Returns 500 Error
- Check Railway logs for the API service
- Verify DATABASE_PATH is `/app/data/kite_db.sqlite`
- Ensure volume is mounted at `/app/data`

### Frontend Can't Connect to API
- Check VITE_API_URL is set correctly
- Verify CORS: check DASHBOARD_URL in API variables
- Test API health endpoint directly

### Database Resets on Restart
- Ensure volume is created and mounted
- Check DATABASE_PATH points to volume location
- Verify volume size is sufficient (1GB+)

### Build Fails
- Check Railway logs for error messages
- Verify railway.toml exists in correct directory
- Ensure package.json has all dependencies

### CORS Errors
- Add frontend URL to API DASHBOARD_URL variable
- Restart API service after variable changes
- Check Flask CORS configuration in api/app.py

---

## Updating the Application

To deploy updates:

**Option 1: Git Push (if auto-deploy enabled)**
```bash
git add .
git commit -m "feat: update feature"
git push origin main
# Railway auto-deploys
```

**Option 2: Manual Railway CLI**
```bash
cd api        # or frontend, or marketing
railway up
```

**Option 3: Railway Dashboard**
- Click on service → **Deployments** → **Deploy**

---

## Rollback

To rollback to a previous deployment:

1. Go to Railway dashboard → Service
2. Click **Deployments**
3. Find previous successful deployment
4. Click **⋯** → **Redeploy**

---

## Backup Database

To backup your SQLite database:

```bash
# SSH into Railway service
railway run bash

# Inside container
cp /app/data/kite_db.sqlite /tmp/backup.sqlite

# Download locally (outside container)
railway run --service api cat /app/data/kite_db.sqlite > backup.sqlite
```

---

## Migration from Vercel

If you're migrating from Vercel:

1. Deploy all services to Railway (follow steps above)
2. Test thoroughly on Railway URLs
3. Update any external integrations to use new URLs
4. Once verified, delete Vercel projects
5. Archive vercel.json files (already done in this guide)

---

## Next Steps

After successful deployment:

1. Set up custom domains (optional)
2. Enable auto-deploy on GitHub push
3. Configure monitoring and alerts
4. Set up database backup schedule
5. Review Railway usage dashboard regularly

---

## Support & Resources

- Railway Docs: https://docs.railway.app
- Railway Discord: https://discord.gg/railway
- Railway Status: https://status.railway.app
- Railway CLI Docs: https://docs.railway.app/develop/cli

---

## Summary Checklist

- [ ] Railway CLI installed and logged in
- [ ] Backend API deployed with volume mounted
- [ ] API environment variables configured
- [ ] Dashboard deployed and connected to API
- [ ] Marketing site deployed
- [ ] All services have public URLs
- [ ] CORS configured correctly (no errors in console)
- [ ] Database persists after API restart
- [ ] Auto-deploy configured (optional)
- [ ] Custom domains added (optional)

**Congratulations! Your InvestEz app is now fully deployed on Railway! 🚂**
