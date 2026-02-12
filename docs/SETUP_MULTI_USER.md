# Multi-User Authentication Setup Guide

This guide will help you set up InvestEz with Google OAuth for user authentication and per-user broker credentials.

## Architecture Overview

**Two-Level Authentication:**
1. **User Authentication** (Google OAuth): Users sign in with their Google account
2. **Broker Authentication** (Kite OAuth): Users connect their broker accounts

**Data Flow:**
- Users → Google OAuth → Session (JWT cookie)
- Users configure broker API credentials → Encrypted storage in SQLite
- Users authenticate with broker → Access token stored per user
- Portfolio data fetched using user-specific credentials

## Prerequisites

1. Python 3.10+
2. Node.js 18+
3. Google Cloud project with OAuth 2.0 credentials

## Step 1: Install Dependencies

### Backend
```bash
pip install -r requirements.txt
```

New dependencies added:
- `cryptography>=41.0.0` - For encrypting broker credentials
- `PyJWT>=2.8.0` - For JWT session tokens

### Frontend
```bash
cd frontend
npm install
```

## Step 2: Configure Google OAuth

### 2.1 Google Cloud Console

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Select your project (or create one)
3. Go to **APIs & Services → Credentials**

### 2.2 Configure OAuth Consent Screen

- Navigate to **OAuth consent screen**
- User Type: **External**
- App name: **InvestEz**
- User support email: Your email
- Developer contact: Your email
- Authorized domains: `railway.app` (for production)
- Scopes: `email`, `profile`, `openid`
- Save and continue

### 2.3 Create OAuth 2.0 Client ID

1. Click **Create Credentials → OAuth 2.0 Client ID**
2. Application type: **Web application**
3. Name: **InvestEz Web Client**

4. **Authorized JavaScript origins:**
   ```
   http://localhost:3000
   http://127.0.0.1:5000
   https://dashboard-production-b3df.up.railway.app
   https://api-production-9507.up.railway.app
   ```

5. **Authorized redirect URIs:**
   ```
   http://127.0.0.1:5000/api/auth/google/callback
   https://api-production-9507.up.railway.app/api/auth/google/callback
   ```

6. Click **Create**
7. **Copy the Client ID and Client Secret**

## Step 3: Configure Environment Variables

### 3.1 Generate Encryption Keys

Generate a database encryption key:
```bash
python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"
```

Generate a JWT secret key:
```bash
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

### 3.2 Update .env File

Copy `.env.example` to `.env` and fill in the values:

```bash
cp .env.example .env
```

Edit `.env`:
```env
# Anthropic API
ANTHROPIC_API_KEY=your_anthropic_api_key

# Google OAuth (User Authentication)
GOOGLE_CLIENT_ID=your-google-client-id-from-step-2
GOOGLE_CLIENT_SECRET=your-google-client-secret-from-step-2
JWT_SECRET_KEY=your-generated-jwt-secret

# Frontend URL for CORS and redirects
FRONTEND_URL=http://localhost:3000

# Database encryption key (for encrypting broker credentials)
DB_ENCRYPTION_KEY=your-generated-fernet-key
```

**Note:** Remove the old `KITE_API_KEY` and `KITE_API_SECRET` from your `.env` - these are now stored per-user in the database.

## Step 4: Initialize Database

The database will be automatically initialized on first run. It creates:
- `users` table (Google user info)
- `brokers` table (available brokers - seeded with Kite)
- `broker_credentials` table (user-specific broker credentials)

To manually initialize or reset:
```bash
python -c "from database.db import init_db; init_db()"
```

To reset database (⚠️ deletes all data):
```bash
python -c "from database.db import reset_db; reset_db()"
```

## Step 5: Start Development Servers

### Backend
```bash
# Terminal 1
flask --app api.app run --port 5000 --debug
```

### Frontend
```bash
# Terminal 2
cd frontend
npm run dev
```

Frontend will be available at: `http://localhost:3000`
Backend API will be available at: `http://127.0.0.1:5000`

## Step 6: Test the Flow

### 6.1 User Login
1. Open `http://localhost:3000`
2. You should see the Google login screen
3. Click "Sign in with Google"
4. A popup will open for Google OAuth
5. After successful login, you'll be redirected to the dashboard

### 6.2 Configure Broker
1. You'll see two tiles: "Configure Brokers" and "Authenticate"
2. Click "Configure Brokers"
3. Click "Configure" button for Kite
4. Enter your Kite API Key and API Secret
5. Click "Save Credentials"

### 6.3 Authenticate with Broker
1. Click "Authenticate" on the Kite broker
2. You'll be redirected to Kite login
3. After login, you'll be redirected back
4. Your portfolio dashboard will load

### 6.4 Access Broker Management
1. Once authenticated, click on your profile icon (top right)
2. Click "Brokers"
3. You can now manage your broker connections

## Step 7: Production Deployment

### Railway Environment Variables

Add these to your Railway services:

**API Service:**
```env
GOOGLE_CLIENT_ID=your-client-id
GOOGLE_CLIENT_SECRET=your-client-secret
JWT_SECRET_KEY=your-jwt-secret
DB_ENCRYPTION_KEY=your-encryption-key
FRONTEND_URL=https://dashboard-production-b3df.up.railway.app
ANTHROPIC_API_KEY=your-anthropic-key
```

**Dashboard Service:**
```env
VITE_API_URL=https://api-production-9507.up.railway.app/api
```

### Update Google OAuth Settings

After deployment, add production URLs to Google Cloud Console:

**Authorized JavaScript origins:**
- Add your Railway frontend URL
- Add your Railway API URL

**Authorized redirect URIs:**
- Add `https://api-production-9507.up.railway.app/api/auth/google/callback`

## API Endpoints

### User Authentication
- `GET /api/auth/google/login` - Get Google OAuth URL
- `GET /api/auth/google/callback` - Handle Google OAuth callback
- `GET /api/auth/google/me` - Get current user info
- `POST /api/auth/google/logout` - Logout user

### Broker Management
- `GET /api/brokers` - List all brokers with user's status
- `POST /api/brokers/:broker_id/credentials` - Save broker credentials
- `DELETE /api/brokers/:broker_id/credentials` - Delete broker credentials
- `GET /api/brokers/:broker_id/credentials` - Get credential status

### Broker Authentication (Kite)
- `GET /api/auth/login-url` - Get Kite OAuth URL (requires user auth)
- `POST /api/auth/callback` - Handle Kite OAuth callback (requires user auth)
- `GET /api/auth/status` - Get auth status (user + broker)
- `POST /api/auth/logout` - Logout from broker
- `GET /api/auth/profile` - Get broker profile

## Database Schema

### users
```sql
id INTEGER PRIMARY KEY
google_id TEXT UNIQUE NOT NULL
email TEXT NOT NULL
name TEXT
profile_picture TEXT
created_at TIMESTAMP
updated_at TIMESTAMP
```

### brokers
```sql
id INTEGER PRIMARY KEY
name TEXT NOT NULL
broker_id TEXT UNIQUE NOT NULL (e.g., 'kite')
oauth_enabled INTEGER DEFAULT 1
created_at TIMESTAMP
```

### broker_credentials
```sql
id INTEGER PRIMARY KEY
user_id INTEGER (FK to users)
broker_id INTEGER (FK to brokers)
api_key TEXT NOT NULL
api_secret_encrypted TEXT NOT NULL (Fernet encrypted)
access_token_encrypted TEXT (Fernet encrypted)
status TEXT ('configured' | 'authenticated')
created_at TIMESTAMP
updated_at TIMESTAMP
UNIQUE(user_id, broker_id)
```

## Security Notes

1. **Encryption**: All sensitive data (API secrets, access tokens) are encrypted using Fernet symmetric encryption
2. **JWT Tokens**: User sessions use JWT with 30-day expiry, stored in httpOnly cookies
3. **CORS**: Only configured origins can access the API
4. **Authentication Required**: All broker and portfolio endpoints require valid user authentication

## Troubleshooting

### "DB_ENCRYPTION_KEY not set"
- Make sure you've generated and set the encryption key in `.env`

### "Google OAuth not configured"
- Verify `GOOGLE_CLIENT_ID` and `GOOGLE_CLIENT_SECRET` are set
- Check that redirect URIs match exactly in Google Console

### "Kite credentials not configured"
- User needs to configure their Kite API credentials first
- Go to Configure Brokers → Configure → Enter credentials

### Database issues
- Delete `investez.db` and restart to reinitialize
- Or run `python -c "from database.db import reset_db; reset_db()"`

## Migration from Single-User

If you were using the old single-user system:

1. Note down your Kite API credentials from `.env`
2. Pull the latest code with multi-user support
3. Install new dependencies
4. Configure Google OAuth
5. Set up new environment variables
6. Run the app and login with Google
7. Re-enter your Kite credentials in the Configure Brokers section

The old `.kite_token` and `.kite_profile` files are kept for backward compatibility but are no longer the primary storage.

## Support

For issues or questions:
- Check the [GitHub Issues](https://github.com/your-repo/investez/issues)
- Review the logs for error messages
- Verify all environment variables are set correctly
