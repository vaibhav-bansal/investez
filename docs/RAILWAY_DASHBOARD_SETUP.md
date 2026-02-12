# Railway Dashboard Deployment (Recommended)

Since the Railway CLI is experiencing connectivity issues, use the web dashboard for deployment.

## Step-by-Step Dashboard Deployment

### 1. Create New Project

1. Go to https://railway.app/dashboard
2. Click **"New Project"**
3. Select **"Deploy from GitHub repo"**
4. Authorize Railway to access your GitHub (if not already done)
5. Select repository: `vaibhav-bansal/investez`

### 2. Configure Services

Railway will create one service initially. You need to add two more services for a total of three.

---

## Service 1: Backend API

### Initial Setup
1. Railway creates the first service automatically
2. Click on the service → **Settings**
3. Change **Service Name**: `investez-api`
4. Set **Root Directory**: `api`

### Build Configuration
Under **Settings** → **Build**:
- **Builder**: Nixpacks (automatic)
- **Watch Paths**: `api/**`

### Start Command
Under **Settings** → **Deploy**:
```
gunicorn --bind 0.0.0.0:$PORT --workers 2 --timeout 120 api.app:app
```

### Environment Variables
Click **Variables** tab and add:

```
PORT=5000
SECRET_KEY=<generate-random-32-character-string>
DATABASE_PATH=/app/data/kite_db.sqlite
KITE_API_KEY=<your-kite-api-key>
KITE_API_SECRET=<your-kite-api-secret>
KITE_ACCESS_TOKEN=<your-kite-access-token>
PYTHONUNBUFFERED=1
```

**Generate SECRET_KEY**:
```bash
# In your terminal
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

### Add Volume (Important!)
1. Go to **Settings** → **Volumes**
2. Click **"New Volume"**
3. Mount Path: `/app/data`
4. Size: 1 GB

### Generate Domain
1. Go to **Settings** → **Networking**
2. Click **"Generate Domain"**
3. Copy the URL (e.g., `investez-api-production.up.railway.app`)
4. Save this URL - you'll need it for the frontend

### Deploy
1. Click **"Deploy"** button
2. Wait for deployment to complete (check **Deployments** tab)
3. Test the health endpoint:
   ```
   https://your-api-url.up.railway.app/api/health
   ```
   Should return: `{"status": "ok"}`

---

## Service 2: Dashboard Frontend

### Add New Service
1. In your project dashboard, click **"New"** → **"GitHub Repo"**
2. Select `vaibhav-bansal/investez` again
3. Railway creates a new service

### Configure Service
1. Click on the new service → **Settings**
2. Change **Service Name**: `investez-dashboard`
3. Set **Root Directory**: `frontend`

### Build Configuration
Under **Settings** → **Build**:
- Builder: Nixpacks (automatic)
- Build Command: `npm install && npm run build`
- Watch Paths: `frontend/**`

### Start Command
Under **Settings** → **Deploy**:
```
npx serve -s dist -l $PORT
```

### Environment Variables
Click **Variables** tab and add:

```
VITE_API_URL=https://your-api-url.up.railway.app/api
NODE_ENV=production
```

**Replace `your-api-url.up.railway.app` with the actual URL from Service 1**

### Generate Domain
1. Go to **Settings** → **Networking**
2. Click **"Generate Domain"**
3. Copy the URL (e.g., `investez-dashboard-production.up.railway.app`)

### Update API CORS
Now go back to **Service 1 (API)**:
1. Click **Variables**
2. Add new variable:
   ```
   DASHBOARD_URL=https://your-dashboard-url.up.railway.app
   ```
3. The service will auto-redeploy

### Deploy Dashboard
1. Click **"Deploy"** button
2. Wait for deployment
3. Visit your dashboard URL and verify it loads

---

## Service 3: Marketing Website

### Add New Service
1. In project dashboard, click **"New"** → **"GitHub Repo"**
2. Select `vaibhav-bansal/investez` again

### Configure Service
1. Click on the new service → **Settings**
2. Change **Service Name**: `investez-marketing`
3. Set **Root Directory**: `marketing`

### Build Configuration
Under **Settings** → **Build**:
- Builder: Nixpacks (automatic)
- Build Command: `npm install --legacy-peer-deps && npm run build`
- Watch Paths: `marketing/**`

### Start Command
Under **Settings** → **Deploy**:
```
npx serve -s dist -l $PORT
```

### Environment Variables
Click **Variables** tab and add:

```
NODE_ENV=production
```

### Generate Domain
1. Go to **Settings** → **Networking**
2. Click **"Generate Domain"**
3. Copy the URL

### Update API CORS
Go back to **Service 1 (API)**:
1. Click **Variables**
2. Add new variable:
   ```
   MARKETING_URL=https://your-marketing-url.up.railway.app
   ```

### Deploy Marketing
1. Click **"Deploy"** button
2. Wait for deployment
3. Visit your marketing URL

---

## Final Configuration Summary

Your Railway project should have:

```
investez (Project)
├── investez-api
│   ├── Root: api/
│   ├── Volume: /app/data (1GB)
│   ├── Start: gunicorn --bind 0.0.0.0:$PORT --workers 2 api.app:app
│   └── URL: https://investez-api-production.up.railway.app
├── investez-dashboard
│   ├── Root: frontend/
│   ├── Start: npx serve -s dist -l $PORT
│   └── URL: https://investez-dashboard-production.up.railway.app
└── investez-marketing
    ├── Root: marketing/
    ├── Start: npx serve -s dist -l $PORT
    └── URL: https://investez-marketing-production.up.railway.app
```

---

## Enable Auto-Deploy (Optional)

For each service:

1. Go to **Settings** → **Source**
2. Under **Deployment Triggers**:
   - ✅ Enable **"Automatic Deploys"**
   - Branch: `main`
   - Watch Paths: Already configured above

Now every `git push` to main will automatically deploy!

---

## Verification Checklist

Test each service:

### API Health Check
```bash
curl https://your-api-url.up.railway.app/api/health
# Should return: {"status":"ok"}
```

### Dashboard
1. Visit dashboard URL
2. Open browser DevTools → Console
3. Should have no CORS errors
4. API calls should work

### Marketing
1. Visit marketing URL
2. All sections should load
3. Links should work

### Database Persistence
1. Go to API service → **Deployments**
2. Click **"Redeploy"** on current deployment
3. Verify database data persists after restart

---

## Troubleshooting

### Build Fails

**Check Logs**:
1. Click on service
2. Go to **Deployments** tab
3. Click on failed deployment
4. View **Build Logs** and **Deploy Logs**

**Common Issues**:
- Missing dependencies: Check package.json
- Build command incorrect: Verify in Settings → Build
- Root directory wrong: Double-check Settings

### API Returns 500

1. Check **Logs** tab for error messages
2. Verify environment variables are set
3. Check volume is mounted at `/app/data`
4. Verify DATABASE_PATH points to volume

### Frontend CORS Errors

1. Check API **Variables** has `DASHBOARD_URL` set correctly
2. Verify dashboard has `VITE_API_URL` set correctly
3. Check API logs for CORS errors
4. API service should auto-restart when variables change

### Database Resets

1. Ensure volume exists: API service → Settings → Volumes
2. Verify mount path is `/app/data`
3. Check DATABASE_PATH=/app/data/kite_db.sqlite in variables

---

## Update Application

When you make code changes:

1. Commit and push to GitHub:
   ```bash
   git add .
   git commit -m "feat: your changes"
   git push origin main
   ```

2. If auto-deploy is enabled, Railway deploys automatically

3. Or manually deploy:
   - Go to service → **Deployments**
   - Click **"Deploy"** button

---

## Monitor Usage

1. Go to **Project Settings** → **Usage**
2. View current usage and costs
3. Railway shows:
   - Active hours
   - Network egress
   - Monthly cost estimate

Free tier includes $5 credit/month.

---

## Custom Domains (Optional)

For each service:

1. Go to **Settings** → **Networking**
2. Click **"Custom Domain"**
3. Add your domain:
   - API: `api.yourdomain.com`
   - Dashboard: `app.yourdomain.com`
   - Marketing: `yourdomain.com`
4. Update DNS as instructed by Railway
5. Update environment variables with new URLs

---

## Support

- Railway Docs: https://docs.railway.app
- Railway Discord: https://discord.gg/railway
- Railway Status: https://status.railway.app

---

**You're all set! Your InvestEz app is now fully deployed on Railway! 🚂**
