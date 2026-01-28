# InvestEz Quick Start

Get InvestEz running locally or deployed to Railway in minutes.

## Local Development (5 minutes)

### Prerequisites
- Python 3.9+
- Node.js 18+
- npm or yarn

### Setup

1. **Clone and Install**
   ```bash
   git clone https://github.com/vaibhav-bansal/investez.git
   cd investez
   pip install -r requirements.txt
   ```

2. **Configure Environment**
   ```bash
   cp .env.example .env
   # Edit .env with your Kite API credentials
   ```

3. **Start Services**
   ```bash
   # Terminal 1: Backend API
   cd api
   flask --app app run --port 5000 --debug

   # Terminal 2: Dashboard
   cd frontend
   npm install
   npm run dev

   # Terminal 3: Marketing Site
   cd marketing
   npm install --legacy-peer-deps
   npm run dev
   ```

4. **Access Applications**
   - Marketing: http://localhost:5173
   - Dashboard: http://localhost:3000
   - API: http://localhost:5000/api/health

## Deploy to Railway (15 minutes)

### Prerequisites
- Railway account ([railway.app](https://railway.app))
- Git repository

### Deployment Steps

1. **Install Railway CLI**
   ```bash
   npm install -g @railway/cli
   railway login
   ```

2. **Initialize Project**
   ```bash
   railway init
   # Name: investez
   ```

3. **Deploy Backend First**
   ```bash
   cd api
   railway up
   ```

   Then in Railway dashboard:
   - Add volume: `/app/data` (1GB)
   - Set environment variables (see api/.env.example)
   - Generate domain and copy URL

4. **Deploy Dashboard**
   ```bash
   cd ../frontend
   railway up
   ```

   Set environment variable:
   ```
   VITE_API_URL=https://your-api.up.railway.app/api
   ```

5. **Deploy Marketing**
   ```bash
   cd ../marketing
   railway up
   ```

6. **Update API CORS**
   Add to API environment variables:
   ```
   DASHBOARD_URL=https://your-dashboard.up.railway.app
   MARKETING_URL=https://your-marketing.up.railway.app
   ```

**Done!** All services are now deployed.

## Detailed Guides

- **Complete Railway Guide**: [RAILWAY_DEPLOYMENT.md](./RAILWAY_DEPLOYMENT.md)
- **Full Documentation**: [DEPLOYMENT.md](./DEPLOYMENT.md)

## Troubleshooting

### Port Already in Use
```bash
# Kill process on port 5000
lsof -ti:5000 | xargs kill -9
```

### CORS Errors
- Ensure API DASHBOARD_URL matches your frontend URL
- Check Flask CORS configuration in api/app.py

### Database Not Persisting (Railway)
- Verify volume is mounted at `/app/data`
- Check DATABASE_PATH=/app/data/kite_db.sqlite

## Next Steps

After getting started:
1. Configure Kite API credentials
2. Test portfolio data fetching
3. Customize branding and colors
4. Set up custom domains (optional)

## Support

- GitHub Issues: Report bugs and request features
- Railway Docs: https://docs.railway.app
- Kite API Docs: https://kite.trade/docs

**Happy investing! 📈**
