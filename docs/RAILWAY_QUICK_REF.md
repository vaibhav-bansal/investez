# Railway Deployment Quick Reference

**Use Railway Dashboard** (CLI has connectivity issues)

## URLs You Need

- Railway Dashboard: https://railway.app/dashboard
- Full Guide: [RAILWAY_DASHBOARD_SETUP.md](./RAILWAY_DASHBOARD_SETUP.md)

---

## Quick Deploy Steps

### 1. Create Project
https://railway.app/dashboard → New Project → Deploy from GitHub → Select `investez`

### 2. Configure 3 Services

| Service | Root Dir | Start Command | Domain Var |
|---------|----------|---------------|------------|
| **API** | `api` | `gunicorn --bind 0.0.0.0:$PORT --workers 2 api.app:app` | Generate & copy |
| **Dashboard** | `frontend` | `npx serve -s dist -l $PORT` | Generate & copy |
| **Marketing** | `marketing` | `npx serve -s dist -l $PORT` | Generate |

### 3. Environment Variables

**API Service**:
```bash
PORT=5000
SECRET_KEY=<random-32-chars>
DATABASE_PATH=/app/data/kite_db.sqlite
DASHBOARD_URL=<dashboard-domain-from-step-2>
MARKETING_URL=<marketing-domain-from-step-2>
KITE_API_KEY=<your-key>
KITE_API_SECRET=<your-secret>
KITE_ACCESS_TOKEN=<your-token>
PYTHONUNBUFFERED=1
```

**Dashboard Service**:
```bash
VITE_API_URL=<api-domain-from-step-2>/api
NODE_ENV=production
```

**Marketing Service**:
```bash
NODE_ENV=production
```

### 4. Add Volume to API
Settings → Volumes → New Volume
- Mount Path: `/app/data`
- Size: 1 GB

### 5. Deploy All Services
Click "Deploy" button on each service

---

## Generate SECRET_KEY

```bash
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

---

## Test Deployment

```bash
# Test API
curl https://your-api.up.railway.app/api/health

# Visit Dashboard
# Open browser to: https://your-dashboard.up.railway.app

# Visit Marketing
# Open browser to: https://your-marketing.up.railway.app
```

---

## File Locations

```
api/railway.toml          # Already configured
frontend/railway.toml     # Already configured
marketing/railway.toml    # Already configured
api/.env.example          # Template for variables
frontend/.env.example     # Template for variables
```

---

## Need Help?

**Detailed Guide**: [RAILWAY_DASHBOARD_SETUP.md](./RAILWAY_DASHBOARD_SETUP.md)
**Full Documentation**: [RAILWAY_DEPLOYMENT.md](./RAILWAY_DEPLOYMENT.md)
