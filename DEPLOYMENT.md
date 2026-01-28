# InvestEz Deployment Guide

**Updated: January 2026**

> **Note**: This project has been migrated to Railway for simplified deployment.
> See [RAILWAY_DEPLOYMENT.md](./RAILWAY_DEPLOYMENT.md) for the complete guide.

## Quick Start

InvestEz is deployed entirely on Railway:

- **Marketing Website**: Static React site
- **Dashboard Frontend**: React + Vite app
- **Backend API**: Flask + SQLite with persistent storage

## Why Railway?

Railway provides a unified platform for all three services:

- ✅ Single dashboard for all deployments
- ✅ Persistent volume storage for SQLite
- ✅ Automatic HTTPS and SSL
- ✅ Simple environment variable management
- ✅ Auto-deploy from Git
- ✅ $5/month free credit

## Deployment Overview

```
┌─────────────────────────────────────┐
│  Marketing (Railway)                │
│  investez-marketing.up.railway.app  │
└─────────────────────────────────────┘

┌─────────────────────────────────────┐
│  Dashboard (Railway)                │
│  investez-dashboard.up.railway.app  │
└──────────────┬──────────────────────┘
               │
               ↓
┌─────────────────────────────────────┐
│  Backend API (Railway)              │
│  investez-api.up.railway.app        │
│  - Persistent SQLite database       │
└─────────────────────────────────────┘
```

## Getting Started

1. **Install Railway CLI**:
   ```bash
   npm install -g @railway/cli
   railway login
   ```

2. **Deploy Services**:
   Each folder has a `railway.toml` configuration file.
   ```bash
   # Deploy API first
   cd api && railway up

   # Deploy dashboard
   cd ../frontend && railway up

   # Deploy marketing
   cd ../marketing && railway up
   ```

3. **Configure Environment Variables**:
   See `.env.example` files in each directory for required variables.

## Detailed Instructions

For step-by-step deployment instructions, see:

**[📘 RAILWAY_DEPLOYMENT.md](./RAILWAY_DEPLOYMENT.md)**

This comprehensive guide covers:
- Complete setup walkthrough
- Environment variable configuration
- Volume mounting for database
- Custom domain setup
- Monitoring and troubleshooting
- Cost breakdown and optimization

## Local Development

```bash
# Backend (Terminal 1)
cd api
flask --app app run --port 5000 --debug

# Dashboard (Terminal 2)
cd frontend
npm run dev

# Marketing (Terminal 3)
cd marketing
npm run dev
```

## Cost Estimate

Railway Free Tier includes:
- $5 credit/month
- Covers light usage for all 3 services
- Estimated cost after credit: $10-25/month

## Project Structure

```
investez/
├── api/
│   ├── railway.toml          # Railway config
│   ├── .env.example          # Environment template
│   └── app.py                # Flask app
├── frontend/
│   ├── railway.toml          # Railway config
│   ├── .env.example          # Environment template
│   └── package.json
├── marketing/
│   ├── railway.toml          # Railway config
│   └── package.json
└── RAILWAY_DEPLOYMENT.md     # Complete guide
```

## Migration Notes

This project was previously configured for Vercel (frontend) + Railway (backend).
We've consolidated everything to Railway for simplicity.

Old Vercel configurations are preserved in `archive/vercel-configs/` for reference.

## Support

- Railway Docs: https://docs.railway.app
- Railway Discord: https://discord.gg/railway
- Project Issues: Use GitHub issues for bugs/features

---

**For complete deployment instructions, see [RAILWAY_DEPLOYMENT.md](./RAILWAY_DEPLOYMENT.md)**
