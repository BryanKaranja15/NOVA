# Supabase Setup - Quick Guide

## Your Supabase Credentials

✅ **Project URL**: `https://ntnkgdwhhyhysifnurfi.supabase.co`  
✅ **Anon Key**: Configured  
✅ **Service Role Key**: Configured  
❌ **Database Password**: **NEEDED** (see below)

## Get Your Database Password

1. Go to: https://app.supabase.com/project/ntnkgdwhhyhysifnurfi
2. Click **Settings** (gear icon in left sidebar)
3. Click **Database** in the settings menu
4. Scroll to **Database password** section
5. If you don't see it, click **Reset database password** or **Reveal password**
6. Copy the password

## Create Your `.env` File

Create a `.env` file in the project root with:

```bash
# Supabase Configuration
SUPABASE_URL=https://ntnkgdwhhyhysifnurfi.supabase.co
SUPABASE_ANON_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Im50bmtnZHdoaHloeXNpZm51cmZpIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NjEwMDYyMjMsImV4cCI6MjA3NjU4MjIyM30.FZ-AIj7tqqrgRibsAQPtffrrDmPrQt95GwO2khASY6s
SUPABASE_SERVICE_ROLE_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Im50bmtnZHdoaHloeXNpZm51cmZpIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc2MTAwNjIyMywiZXhwIjoyMDc2NTgyMjIzfQ.U9ApmCZcWFdiJ24G6yon7X8vOIveZ0XI8kTp8ryLpmI

# Database Connection (REPLACE YOUR_PASSWORD_HERE with actual password)
DATABASE_URL=postgresql://postgres:YOUR_PASSWORD_HERE@db.ntnkgdwhhyhysifnurfi.supabase.co:5432/postgres

# OR use individual components:
# SUPABASE_DB_PASSWORD=YOUR_PASSWORD_HERE
# SUPABASE_DB_HOST=db.ntnkgdwhhyhysifnurfi.supabase.co
# SUPABASE_DB_USER=postgres
# SUPABASE_DB_NAME=postgres
# SUPABASE_DB_PORT=5432
```

## Verify Connection

After adding your database password, test the connection:

```bash
python scripts/verify_database.py
```

## Next Steps

1. ✅ Add database password to `.env` file
2. ✅ Verify connection works
3. ✅ Create tables: Copy `database_schema.sql` into Supabase SQL Editor
4. ✅ Test database operations

## Database Connection String Format

Your database connection string should look like:
```
postgresql://postgres:PASSWORD@db.ntnkgdwhhyhysifnurfi.supabase.co:5432/postgres
```

Where:
- `postgres` = username (default)
- `PASSWORD` = your database password (from Supabase Dashboard)
- `db.ntnkgdwhhyhysifnurfi.supabase.co` = database host
- `5432` = port (default)
- `postgres` = database name (default)


