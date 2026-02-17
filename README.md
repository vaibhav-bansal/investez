# InvestEz

All your investments in one place. Consolidate portfolios from multiple brokers and get AI-powered research and insights.

## What InvestEz Does

InvestEz solves two critical problems for Indian retail investors:

**Problem 1: Scattered Investments**
Most investors have accounts with multiple brokers - Zerodha, Groww, Upstox, and more. Your investments are scattered across different platforms, making it impossible to see the complete picture. You can't manage what you can't see.

**Problem 2: Complex Research**
Investment research is complex, jargon-heavy, and time-consuming. Most retail investors don't have access to the tools and insights that institutional investors use daily.

## Solution

**First, visibility** - InvestEz consolidates all your investments from multiple brokers into one unified dashboard. See everything in one place - your complete portfolio, performance, allocation, and trends.

**Second, intelligence** - We add AI-powered research and insights. Ask questions in plain language and get clear, actionable answers. No jargon, no complexity - just the information you need to make smarter decisions.

## Current Status

Users can currently fetch portfolio from Zerodha and Groww together and see merged portfolio analytics.

## Tech Stack

**Backend (Python Flask)**
- Flask web framework
- SQLite database
- Google OAuth + Zerodha Kite OAuth for authentication
- Kite Connect API for Zerodha integration
- BeautifulSoup4 + lxml for web scraping
- Anthropic Claude API for AI insights
- Deployed on Railway.app

**Frontend Dashboard (React + TypeScript)**
- React 18 with Vite
- Tailwind CSS for styling
- React Query for data fetching
- Recharts for portfolio visualization
- Axios for API calls

**Marketing Website (React + TypeScript)**
- React 19 with Vite
- Tailwind CSS
- Lucide React icons

## Project Structure

```
investez/
├── api/              # Flask API backend
├── frontend/         # Main dashboard React app
├── marketing/        # Marketing website
├── models/           # Pydantic models
├── services/         # Business logic services
└── tools/            # Integration tools (Kite, Groww, Screener)
```

## Developer Setup

### Prerequisites

- Python 3.9+
- Node.js 18+
- Git

### Backend Setup

1. Navigate to the api directory:
   ```bash
   cd api
   ```

2. Create a virtual environment and activate it:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Create a .env file with required environment variables (see .env.example)

5. Run the Flask development server:
   ```bash
   flask run
   ```

### Frontend Dashboard Setup

1. Navigate to the frontend directory:
   ```bash
   cd frontend
   ```

2. Install dependencies:
   ```bash
   npm install
   ```

3. Start the development server:
   ```bash
   npm run dev
   ```

### Marketing Website Setup

1. Navigate to the marketing directory:
   ```bash
   cd marketing
   ```

2. Install dependencies:
   ```bash
   npm install
   ```

3. Start the development server:
   ```bash
   npm run dev
   ```

## Environment Variables

Key environment variables needed for the API:
- GOOGLE_CLIENT_ID, GOOGLE_CLIENT_SECRET - For Google OAuth
- KITE_API_KEY - For Zerodha Kite integration
- ANTHROPIC_API_KEY - For AI features
- DATABASE_URL - Database connection string

See .env.example for the complete list.

## Contributing

We welcome contributions. Please ensure your code passes type-check and tests before submitting.
