"""
Script to clear/reset the database.

This script will:
1. Drop all existing tables
2. Recreate all tables from the schema
3. Optionally run the schema SQL file

Usage:
    python scripts/clear_database.py
    python scripts/clear_database.py --confirm  # Skip confirmation prompt
"""

import os
import sys
import argparse
from pathlib import Path

# Add parent directory to path to import database config
sys.path.insert(0, str(Path(__file__).parent.parent))

from flask import Flask
from database.db_config import init_db, reset_database, drop_tables, create_tables
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


def clear_database(confirm=False, recreate=True):
    """
    Clear the database by dropping and optionally recreating all tables.
    
    Args:
        confirm: If True, skip confirmation prompt
        recreate: If True, recreate tables after dropping
    """
    # Create a minimal Flask app for database operations
    app = Flask(__name__)
    
    # Initialize database
    try:
        db = init_db(app)
        print("✅ Database connection established")
    except Exception as e:
        print(f"❌ Failed to connect to database: {e}")
        print("\nPlease check your .env file has the correct database credentials:")
        print("  - DATABASE_URL (PostgreSQL connection string)")
        print("  - Or SUPABASE_URL + SUPABASE_DB_PASSWORD")
        print("  - Or POSTGRES_HOST, POSTGRES_USER, POSTGRES_PASSWORD, etc.")
        return False
    
    # Confirm before proceeding
    if not confirm:
        print("\n⚠️  WARNING: This will DELETE ALL DATA in the database!")
        print("   All tables will be dropped and recreated.")
        response = input("\nType 'yes' to continue, or anything else to cancel: ")
        if response.lower() != 'yes':
            print("❌ Operation cancelled")
            return False
    
    try:
        if recreate:
            print("\n🔄 Resetting database...")
            reset_database(app)
            print("\n✅ Database cleared and reset successfully!")
        else:
            print("\n🗑️  Dropping all tables...")
            drop_tables(app)
            print("\n✅ All tables dropped successfully!")
        
        return True
    except Exception as e:
        print(f"\n❌ Error during database operation: {e}")
        import traceback
        traceback.print_exc()
        return False


def run_schema_sql(app):
    """
    Run the database_schema.sql file to create tables.
    
    Args:
        app: Flask application instance
    """
    schema_file = Path(__file__).parent.parent / "database_schema.sql"
    
    if not schema_file.exists():
        print(f"⚠️  Schema file not found: {schema_file}")
        return False
    
    try:
        from database.db_config import db
        import psycopg2
        from urllib.parse import urlparse
        
        # Get database URL
        database_url = app.config.get('SQLALCHEMY_DATABASE_URI')
        if not database_url:
            print("❌ No database URL configured")
            return False
        
        # Parse connection string
        parsed = urlparse(database_url)
        
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
        
        # Read and execute SQL file
        print(f"📄 Reading schema file: {schema_file}")
        with open(schema_file, 'r') as f:
            sql = f.read()
        
        print("🔨 Executing schema SQL...")
        cursor.execute(sql)
        
        cursor.close()
        conn.close()
        
        print("✅ Schema SQL executed successfully!")
        return True
        
    except ImportError:
        print("⚠️  psycopg2 not installed. Install it with: pip install psycopg2-binary")
        print("   Using SQLAlchemy to create tables instead...")
        return False
    except Exception as e:
        print(f"❌ Error running schema SQL: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    parser = argparse.ArgumentParser(description='Clear/reset the database')
    parser.add_argument(
        '--confirm',
        action='store_true',
        help='Skip confirmation prompt (use with caution!)'
    )
    parser.add_argument(
        '--drop-only',
        action='store_true',
        help='Only drop tables, do not recreate them'
    )
    parser.add_argument(
        '--use-sql',
        action='store_true',
        help='Use database_schema.sql file instead of SQLAlchemy models'
    )
    
    args = parser.parse_args()
    
    print("=" * 60)
    print("Database Clear/Reset Script")
    print("=" * 60)
    
    # Check for Supabase keys
    supabase_keys = os.getenv('SUPABASE_SERVICE_ROLE_KEY') or os.getenv('SUPABASE_API_KEY')
    supabase_anon = os.getenv('SUPABASE_ANON_KEY')
    
    if supabase_keys or supabase_anon:
        print("\n📋 Supabase credentials found:")
        if supabase_keys:
            print(f"   ✅ Service Role Key: {supabase_keys[:20]}...")
        if supabase_anon:
            print(f"   ✅ Anon Key: {supabase_anon[:20]}...")
    else:
        print("\n⚠️  No Supabase keys found in environment")
        print("   Using PostgreSQL connection string instead")
    
    # Clear database
    success = clear_database(
        confirm=args.confirm,
        recreate=not args.drop_only
    )
    
    if success and args.use_sql:
        app = Flask(__name__)
        init_db(app)
        run_schema_sql(app)
    
    if success:
        print("\n" + "=" * 60)
        print("✅ Operation completed successfully!")
        print("=" * 60)
    else:
        print("\n" + "=" * 60)
        print("❌ Operation failed. Check errors above.")
        print("=" * 60)
        sys.exit(1)


if __name__ == '__main__':
    main()


