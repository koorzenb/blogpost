# About

Website for posting blogs. Built with Flask and PostgreSQL (AWS Aurora via Vercel).

First user to register will be admin. Subsequent users will be regular users.

## Database Architecture

- **Local Development**: Uses SQLite (`posts.db`) for easy development
- **Production (Vercel)**: Uses AWS Aurora PostgreSQL with IAM authentication
- **Automatic Switching**: `db_config.py` handles database selection based on environment

---

# Setup Guide: PostgreSQL with Vercel

## Prerequisites

- Vercel account
- Vercel CLI installed: `npm install -g vercel`
- Python 3.13+ with virtual environment

## Step 1: Create PostgreSQL Database in Vercel

1. Go to Vercel Dashboard
2. Select your project
3. Navigate to **Storage** tab
4. Click **Create Database** → **Postgres**
5. Choose a database name and region
6. Click **Create**

Vercel will automatically create environment variables for your database connection.

## Step 2: Install Vercel CLI and Link Project

```bash
# Install Vercel CLI (if not already installed)
npm install -g vercel

# Login to Vercel
vercel login

# Link your project (run in project directory)
vercel link
```

## Step 3: Pull Environment Variables

```bash
# Download environment variables from Vercel to .env.local
vercel env pull
```

This creates a `.env.local` file with your database credentials including:
- `PGHOST`, `PGPORT`, `PGDATABASE`, `PGUSER`
- `AWS_REGION`, `AWS_ACCOUNT_ID`, `AWS_ROLE_ARN`
- `VERCEL_OIDC_TOKEN`

## Step 4: Install Python Dependencies

```bash
# Activate virtual environment
py -m venv venv
venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

Key packages installed:
- `psycopg2-binary==2.9.12` - PostgreSQL adapter
- `boto3==1.28.85` - AWS SDK for IAM authentication
- `python-dotenv==1.0.0` - Environment variable management

## Step 5: Configure Database (Already Done)

The following files handle database configuration:

- **`db_config.py`**: Generates database URI with IAM authentication
  - Tries IAM auth for production (Vercel)
  - Falls back to SQLite for local development
  
- **`main.py`**: Updated to use `get_database_uri()` instead of hardcoded DB_URI

## Step 6: Remove Conflicting Environment Variables

```bash
# Remove DB_URI from Vercel production (if it exists)
vercel env rm DB_URI production
```

This ensures the app uses `db_config.py` logic instead of a hardcoded SQLite path.

## Step 7: Create Vercel Configuration

Create `vercel.json` in project root:

```json
{
  "version": 2,
  "builds": [
    {
      "src": "main.py",
      "use": "@vercel/python"
    }
  ],
  "routes": [
    {
      "src": "/(.*)",
      "dest": "main.py"
    }
  ]
}
```

## Step 8: Deploy to Vercel

```bash
# Stage your changes
git add .gitignore main.py requirements.txt db_config.py vercel.json

# Commit changes
git commit -m "Add PostgreSQL support with AWS Aurora IAM authentication"

# Push to GitHub
git push origin main

# Deploy to Vercel production
vercel --prod
```

---

# Local Development

```bash
# Activate virtual environment
venv\Scripts\activate

# Run Flask app (uses SQLite locally)
python main.py
```

The app will run on `http://127.0.0.1:5002` and use SQLite for local development.

---

# How It Works

## Database Selection Logic

The `db_config.py` file automatically selects the appropriate database:

1. **On Vercel (Production)**:
   - Uses AWS Aurora PostgreSQL
   - Authenticates via IAM using `VERCEL_OIDC_TOKEN`
   - Generates temporary auth tokens via boto3
   
2. **Locally**:
   - Falls back to SQLite (`posts.db`)
   - No AWS credentials needed for development
   
## Table Creation

Tables are created automatically via SQLAlchemy:

```python
with app.app_context():
    db.create_all()
```

On first deployment, Flask will create:
- `users` table
- `blog_posts` table
- `comments` table

---

# Important Notes

## Environment Variables

- **`.env`**: Local configuration (FLASK_KEY, local DB_URI)
- **`.env.local`**: Vercel credentials (pulled via `vercel env pull`)
- **Never commit** `.env` or `.env.local` files (already in `.gitignore`)

## IAM Authentication vs Password

- Your setup uses **AWS IAM authentication** (no password)
- Vercel manages AWS access via OIDC federation
- You cannot use traditional PostgreSQL password authentication with this setup
- For local PostgreSQL testing, install PostgreSQL locally and update `.env`

## Vercel OIDC Token

The `VERCEL_OIDC_TOKEN` in `.env.local`:
- Is automatically rotated by Vercel
- Valid for limited time (hours)
- Refreshed automatically on deployment
- Run `vercel env pull` periodically to update locally

---

# Troubleshooting

## Issue: ModuleNotFoundError: No module named 'boto3'

**Solution**: Install dependencies in your virtual environment:
```bash
venv\Scripts\activate
pip install -r requirements.txt
```

## Issue: Cannot connect to PostgreSQL locally

**Expected Behavior**: The app falls back to SQLite locally. This is intentional.

**Why**: AWS IAM authentication requires:
- AWS credentials configured locally
- Vercel's OIDC federation only works on Vercel's infrastructure

**For local PostgreSQL testing**: Install PostgreSQL locally and set `DB_PASSWORD` in `.env.local`

## Issue: Tables not created in PostgreSQL

**Solution**: Tables are created on first app run. Check Vercel deployment logs:
```bash
vercel logs <deployment-url>
```

## Issue: Deployment fails with "builds" warning

**This is normal**: The warning about `builds` in `vercel.json` is informational, not an error.

---

# Deployment Checklist

Before deploying:
- [ ] `vercel env pull` - Pull latest environment variables
- [ ] `pip install -r requirements.txt` - Install dependencies
- [ ] Test locally with `python main.py`
- [ ] Commit changes to Git
- [ ] Run `vercel --prod` to deploy

After deployment:
- [ ] Visit production URL
- [ ] Register first user (becomes admin with ID 1)
- [ ] Test creating blog posts
- [ ] Verify data persists after redeployment
