# Database Setup Guide

## Supabase Configuration

### 1. Get Your Supabase Credentials

1. Go to your Supabase project: https://app.supabase.com
2. Navigate to **Settings** → **API**
3. Copy the following:
   - **Project URL** → `SUPABASE_URL`
   - **anon/public key** → `SUPABASE_ANON_KEY`
   - **service_role key** → `SUPABASE_SERVICE_ROLE_KEY`

4. Navigate to **Settings** → **Database**
5. Copy the **Database password** → `SUPABASE_DB_PASSWORD`
6. Note the connection details:
   - Host: `db.xxxxx.supabase.co` (where xxxxx is your project ref)
   - Port: `5432`
   - Database: `postgres`
   - User: `postgres`

### 2. Create `.env` File

Create a `.env` file in the project root with:

```bash
# Supabase Configuration
SUPABASE_URL=https://xxxxx.supabase.co
SUPABASE_SERVICE_ROLE_KEY=your_service_role_key_here
SUPABASE_ANON_KEY=your_anon_key_here
SUPABASE_DB_PASSWORD=your_database_password_here

# Database Connection (PostgreSQL connection string)
# Format: postgresql://user:password@host:port/database
DATABASE_URL=postgresql://postgres:your_password@db.xxxxx.supabase.co:5432/postgres

# Or use individual components:
SUPABASE_DB_USER=postgres
SUPABASE_DB_HOST=db.xxxxx.supabase.co
SUPABASE_DB_NAME=postgres
SUPABASE_DB_PORT=5432
```

### 3. Clear/Reset Database

To clear all data and recreate tables:

```bash
# Interactive (will ask for confirmation)
python scripts/clear_database.py

# Skip confirmation prompt
python scripts/clear_database.py --confirm

# Only drop tables (don't recreate)
python scripts/clear_database.py --drop-only

# Use SQL schema file instead of SQLAlchemy
python scripts/clear_database.py --use-sql
```

### 4. Verify Connection

```bash
python scripts/verify_database.py
```

## Database Schema

The database schema is defined in `database_schema.sql`. This includes:

- `users` - User accounts and sessions
- `weeks` - Program weeks
- `questions` - Questions for each week
- `system_prompts` - LLM prompts
- `week_content_blocks` - Reusable content blocks
- `user_progress` - User progress tracking
- `conversation_states` - Conversation state
- `conversation_messages` - Full message history
- And more...

## Usage in Code

```python
from flask import Flask
from database.db_config import init_db, get_supabase_keys

app = Flask(__name__)
db = init_db(app)

# Get Supabase keys
keys = get_supabase_keys()
print(f"Supabase URL: {keys['url']}")
print(f"API Key: {keys['api_key'][:20]}...")
print(f"Anon Key: {keys['anon_key'][:20]}...")
```


