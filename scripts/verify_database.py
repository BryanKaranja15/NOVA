"""
Script to verify database connection and Supabase credentials.

Usage:
    python scripts/verify_database.py
"""

import os
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from dotenv import load_dotenv
from database.db_config import get_database_url, get_supabase_keys

# Load environment variables
load_dotenv()


def verify_supabase_keys():
    """Verify Supabase API keys are loaded."""
    print("=" * 60)
    print("Supabase Credentials Check")
    print("=" * 60)
    
    keys = get_supabase_keys()
    
    if keys['url']:
        print(f"✅ SUPABASE_URL: {keys['url']}")
    else:
        print("❌ SUPABASE_URL: Not set")
    
    if keys['api_key']:
        masked = keys['api_key'][:20] + "..." + keys['api_key'][-10:] if len(keys['api_key']) > 30 else keys['api_key'][:20] + "..."
        print(f"✅ SUPABASE_SERVICE_ROLE_KEY: {masked}")
    else:
        print("❌ SUPABASE_SERVICE_ROLE_KEY: Not set")
    
    if keys['anon_key']:
        masked = keys['anon_key'][:20] + "..." + keys['anon_key'][-10:] if len(keys['anon_key']) > 30 else keys['anon_key'][:20] + "..."
        print(f"✅ SUPABASE_ANON_KEY: {masked}")
    else:
        print("❌ SUPABASE_ANON_KEY: Not set")
    
    print()
    
    if keys['url'] and keys['api_key'] and keys['anon_key']:
        print("✅ All Supabase credentials are configured!")
        return True
    else:
        print("⚠️  Some Supabase credentials are missing.")
        print("\nTo set them up:")
        print("1. Go to https://app.supabase.com → Your Project → Settings → API")
        print("2. Copy the Project URL, anon key, and service_role key")
        print("3. Add them to your .env file:")
        print("   SUPABASE_URL=https://xxxxx.supabase.co")
        print("   SUPABASE_ANON_KEY=your_anon_key")
        print("   SUPABASE_SERVICE_ROLE_KEY=your_service_role_key")
        return False


def verify_database_connection():
    """Verify database connection string is configured."""
    print("=" * 60)
    print("Database Connection Check")
    print("=" * 60)
    
    try:
        database_url = get_database_url()
        
        if database_url:
            # Mask password in URL
            from urllib.parse import urlparse
            parsed = urlparse(database_url)
            masked_url = f"{parsed.scheme}://{parsed.username}:***@{parsed.hostname}:{parsed.port}{parsed.path}"
            print(f"✅ Database URL configured: {masked_url}")
            
            # Try to connect
            try:
                from flask import Flask
                from database.db_config import init_db
                
                app = Flask(__name__)
                db = init_db(app)
                
                with app.app_context():
                    # Try a simple query
                    from sqlalchemy import text
                    with db.engine.connect() as conn:
                        conn.execute(text("SELECT 1"))
                    print("✅ Database connection successful!")
                    return True
            except Exception as e:
                print(f"❌ Database connection failed: {e}")
                print("\nPlease check:")
                print("  - Database credentials are correct")
                print("  - Database server is running")
                print("  - Network/firewall allows connection")
                return False
        else:
            print("❌ No database URL configured")
            print("\nSet one of the following in your .env file:")
            print("  - DATABASE_URL (PostgreSQL connection string)")
            print("  - SUPABASE_URL + SUPABASE_DB_PASSWORD")
            print("  - POSTGRES_HOST, POSTGRES_USER, POSTGRES_PASSWORD, etc.")
            return False
            
    except Exception as e:
        print(f"❌ Error checking database configuration: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    print("\n" + "=" * 60)
    print("Database & Supabase Verification")
    print("=" * 60 + "\n")
    
    # Check Supabase keys
    supabase_ok = verify_supabase_keys()
    print()
    
    # Check database connection
    db_ok = verify_database_connection()
    print()
    
    # Summary
    print("=" * 60)
    if supabase_ok and db_ok:
        print("✅ All checks passed! Database is ready to use.")
    elif db_ok:
        print("⚠️  Database connection works, but Supabase keys are missing.")
        print("   This is okay if you're using a different PostgreSQL database.")
    else:
        print("❌ Some checks failed. Please fix the issues above.")
    print("=" * 60 + "\n")


if __name__ == '__main__':
    main()

