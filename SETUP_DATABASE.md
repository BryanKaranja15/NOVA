# Quick Database Setup Guide

## 1. Get Supabase Credentials

1. Go to https://app.supabase.com → Your Project
2. **Settings → API**:
   - Copy `Project URL` → `SUPABASE_URL`
   - Copy `anon public` key → `SUPABASE_ANON_KEY`
   - Copy `service_role` key → `SUPABASE_SERVICE_ROLE_KEY`
3. **Settings → Database**:
   - Copy `Database password` → `SUPABASE_DB_PASSWORD`
   - Note the connection string format

## 2. Create `.env` File

Create a `.env` file in the project root:

```bash
# Supabase API Keys
SUPABASE_URL=https://xxxxx.supabase.co
SUPABASE_ANON_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
SUPABASE_SERVICE_ROLE_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...

# Database Connection (PostgreSQL)
# Replace xxxxx with your Supabase project reference
DATABASE_URL=postgresql://postgres:YOUR_PASSWORD@db.xxxxx.supabase.co:5432/postgres

# Or use individual components:
SUPABASE_DB_PASSWORD=your_database_password
SUPABASE_DB_HOST=db.xxxxx.supabase.co
SUPABASE_DB_USER=postgres
SUPABASE_DB_NAME=postgres
SUPABASE_DB_PORT=5432
```

## 3. Verify Setup

```bash
# Check if credentials are loaded correctly
python scripts/verify_database.py
```

## 4. Clear Database

```bash
# Clear all data and recreate tables
python scripts/clear_database.py

# Skip confirmation (use with caution!)
python scripts/clear_database.py --confirm
```

## Quick Reference

### Load Supabase Keys in Python

```python
from database.db_config import get_supabase_keys

keys = get_supabase_keys()
print(keys['url'])        # Supabase project URL
print(keys['api_key'])   # Service role key
print(keys['anon_key'])  # Anon key
```

### Initialize Database in Flask App

```python
from flask import Flask
from database.db_config import init_db

app = Flask(__name__)
db = init_db(app)
```

### Clear Database Programmatically

```python
from flask import Flask
from database.db_config import init_db, reset_database

app = Flask(__name__)
db = init_db(app)

# Clear and recreate all tables
reset_database(app)
```

## Troubleshooting

### Connection Issues

- Check that your `.env` file is in the project root
- Verify database password is correct (Settings → Database)
- Ensure your IP is allowed in Supabase (Settings → Database → Connection Pooling)

### Missing Keys

- Make sure you're using the **service_role** key (not anon key) for admin operations
- Anon key is for client-side operations
- Service role key has full database access

### Import Errors

Install required packages:
```bash
pip install flask-sqlalchemy psycopg2-binary python-dotenv
```


