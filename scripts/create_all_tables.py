"""
Script to create all database tables from the schema file.

This script reads database_schema.sql and executes it against the database.

Usage:
    python scripts/create_all_tables.py
    python scripts/create_all_tables.py --confirm  # Skip confirmation prompt
"""

import os
import sys
import argparse
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from flask import Flask
from database.db_config import init_db, get_database_url
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


def execute_sql_file(sql_file_path, app):
    """
    Execute SQL file against the database.
    
    Args:
        sql_file_path: Path to SQL file
        app: Flask application instance
    """
    try:
        import psycopg2
        from urllib.parse import urlparse
        
        # Get database URL
        database_url = get_database_url()
        if not database_url:
            print("❌ No database URL configured")
            return False
        
        # Parse connection string
        parsed = urlparse(database_url)
        
        print(f"📡 Connecting to database: {parsed.hostname}:{parsed.port}/{parsed.path[1:] if parsed.path else 'postgres'}")
        
        # Connect directly to run SQL
        conn = psycopg2.connect(
            host=parsed.hostname,
            port=parsed.port or 5432,
            user=parsed.username,
            password=parsed.password,
            database=parsed.path[1:] if parsed.path else 'postgres'
        )
        
        conn.autocommit = True
        cursor = conn.cursor()
        
        # Read SQL file
        print(f"📄 Reading schema file: {sql_file_path}")
        with open(sql_file_path, 'r', encoding='utf-8') as f:
            sql = f.read()
        
        # Split SQL into statements (handle multiple statements)
        # PostgreSQL allows executing multiple statements, but we'll do it carefully
        print("🔨 Executing schema SQL...")
        
        # Execute the entire SQL file
        cursor.execute(sql)
        
        cursor.close()
        conn.close()
        
        print("✅ Schema SQL executed successfully!")
        return True
        
    except ImportError:
        print("❌ psycopg2 not installed. Install it with: pip install psycopg2-binary")
        return False
    except Exception as e:
        print(f"❌ Error executing schema SQL: {e}")
        import traceback
        traceback.print_exc()
        return False


def create_tables(confirm=False):
    """
    Create all database tables from schema file.
    
    Args:
        confirm: If True, skip confirmation prompt
    """
    # Find schema file (try final first, then fallback to original)
    schema_file = Path(__file__).parent.parent / "database_schema_final.sql"
    if not schema_file.exists():
        schema_file = Path(__file__).parent.parent / "database_schema.sql"
    
    if not schema_file.exists():
        print(f"❌ Schema file not found: {schema_file}")
        return False
    
    # Create a minimal Flask app for database operations
    app = Flask(__name__)
    
    # Initialize database connection (just to verify)
    try:
        db = init_db(app)
        print("✅ Database connection established")
    except Exception as e:
        print(f"❌ Failed to connect to database: {e}")
        print("\nPlease check your .env file has the correct database credentials:")
        print("  - DATABASE_URL (PostgreSQL connection string)")
        print("  - Or SUPABASE_URL + SUPABASE_DB_PASSWORD")
        return False
    
    # Confirm before proceeding
    if not confirm:
        print("\n⚠️  This will create all database tables, views, functions, and triggers.")
        print("   If tables already exist, some statements may fail.")
        response = input("\nType 'yes' to continue, or anything else to cancel: ")
        if response.lower() != 'yes':
            print("❌ Operation cancelled")
            return False
    
    # Execute SQL file
    success = execute_sql_file(schema_file, app)
    
    if success:
        print("\n" + "=" * 60)
        print("✅ Database tables created successfully!")
        print("=" * 60)
        print("\nNext steps:")
        print("  1. Verify tables were created: SELECT table_name FROM information_schema.tables WHERE table_schema = 'public';")
        print("  2. Load initial data (weeks, questions, prompts)")
        print("  3. Test database connection from your application")
    else:
        print("\n" + "=" * 60)
        print("❌ Failed to create tables. Check errors above.")
        print("=" * 60)
        return False
    
    return True


def verify_tables(app):
    """Verify that tables were created."""
    from database.db_config import db
    
    with app.app_context():
        from sqlalchemy import inspect, text
        
        inspector = inspect(db.engine)
        tables = inspector.get_table_names()
        
        expected_tables = [
            'users', 'weeks', 'questions', 'system_prompts',
            'prompt_variables', 'week_content_blocks', 'user_progress',
            'question_completions', 'conversation_states',
            'conversation_messages', 'user_answers', 'nova_responses',
            'validation_logs', 'system_settings'
        ]
        
        print("\n📊 Verifying tables...")
        print(f"Found {len(tables)} tables in database")
        
        missing = []
        for table in expected_tables:
            if table in tables:
                print(f"  ✅ {table}")
            else:
                print(f"  ❌ {table} (MISSING)")
                missing.append(table)
        
        if missing:
            print(f"\n⚠️  {len(missing)} table(s) are missing: {', '.join(missing)}")
            return False
        else:
            print(f"\n✅ All {len(expected_tables)} expected tables found!")
            return True


def main():
    parser = argparse.ArgumentParser(description='Create all database tables from schema')
    parser.add_argument(
        '--confirm',
        action='store_true',
        help='Skip confirmation prompt'
    )
    parser.add_argument(
        '--verify',
        action='store_true',
        help='Verify tables after creation'
    )
    
    args = parser.parse_args()
    
    print("=" * 60)
    print("Create All Database Tables")
    print("=" * 60)
    print()
    
    # Create tables
    success = create_tables(confirm=args.confirm)
    
    if success and args.verify:
        app = Flask(__name__)
        init_db(app)
        verify_tables(app)
    
    if not success:
        sys.exit(1)


if __name__ == '__main__':
    main()

