"""
Database Configuration for Supabase/PostgreSQL

This module handles database connection setup using Supabase credentials.
"""
import os
from flask_sqlalchemy import SQLAlchemy
from flask import Flask
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Initialize SQLAlchemy
db = SQLAlchemy()

def get_database_url():
    """
    Get database connection URL from environment variables.
    
    Supports:
    1. Direct DATABASE_URL (PostgreSQL connection string)
    2. Supabase credentials (SUPABASE_URL + SUPABASE_DB_PASSWORD)
    3. Individual PostgreSQL credentials
    """
    # Option 1: Direct database URL (highest priority)
    database_url = os.getenv('DATABASE_URL')
    if database_url:
        return database_url
    
    # Option 2: Supabase connection
    supabase_url = os.getenv('SUPABASE_URL')
    supabase_db_password = os.getenv('SUPABASE_DB_PASSWORD')
    supabase_db_user = os.getenv('SUPABASE_DB_USER', 'postgres')
    supabase_db_host = os.getenv('SUPABASE_DB_HOST')
    supabase_db_name = os.getenv('SUPABASE_DB_NAME', 'postgres')
    supabase_db_port = os.getenv('SUPABASE_DB_PORT', '5432')
    
    if supabase_url or supabase_db_host:
        # Extract host from Supabase URL if provided
        if supabase_url and not supabase_db_host:
            # Supabase URL format: https://xxxxx.supabase.co
            # Try connection pooler first (more reliable)
            # Format: aws-0-[region].pooler.supabase.com
            # For now, try the pooler format, or use direct connection if available
            host_part = supabase_url.replace('https://', '').replace('http://', '').split('.')[0]
            # Try connection pooler (port 6543) - more reliable than direct connection
            supabase_db_host = f"aws-0-us-east-1.pooler.supabase.com"
            # If pooler doesn't work, fallback to direct: db.{host_part}.supabase.co
            # But direct connection often has DNS issues, so prefer pooler
        
        if supabase_db_host and supabase_db_password:
            # Use connection pooler port (6543) for better reliability
            pooler_port = os.getenv('SUPABASE_DB_PORT', '6543')
            return f"postgresql://{supabase_db_user}:{supabase_db_password}@{supabase_db_host}:{pooler_port}/{supabase_db_name}"
    
    # Option 3: Individual PostgreSQL credentials
    db_user = os.getenv('POSTGRES_USER', 'postgres')
    db_password = os.getenv('POSTGRES_PASSWORD')
    db_host = os.getenv('POSTGRES_HOST', 'localhost')
    db_port = os.getenv('POSTGRES_PORT', '5432')
    db_name = os.getenv('POSTGRES_DATABASE', 'postgres')
    
    if db_password:
        return f"postgresql://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}"
    
    # Default fallback (will likely fail, but provides a clear error)
    return "postgresql://postgres:postgres@localhost:5432/postgres"


def get_supabase_keys():
    """
    Get Supabase API keys from environment variables.
    
    Returns:
        dict: Dictionary with 'api_key' (service role) and 'anon_key'
    """
    return {
        'api_key': os.getenv('SUPABASE_SERVICE_ROLE_KEY') or os.getenv('SUPABASE_API_KEY'),
        'anon_key': os.getenv('SUPABASE_ANON_KEY'),
        'url': os.getenv('SUPABASE_URL')
    }


def init_db(app: Flask):
    """
    Initialize database connection for Flask app.
    
    Args:
        app: Flask application instance
        
    Returns:
        SQLAlchemy database instance
    """
    database_url = get_database_url()
    
    app.config['SQLALCHEMY_DATABASE_URI'] = database_url
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {
        'pool_pre_ping': True,  # Verify connections before using
        'pool_recycle': 300,     # Recycle connections after 5 minutes
    }
    
    db.init_app(app)
    
    return db


def create_tables(app: Flask):
    """
    Create all database tables.
    
    Args:
        app: Flask application instance
    """
    with app.app_context():
        db.create_all()
        print("✅ Database tables created successfully")


def drop_tables(app: Flask):
    """
    Drop all database tables.
    
    Args:
        app: Flask application instance
    """
    with app.app_context():
        db.drop_all()
        print("✅ All database tables dropped successfully")


def reset_database(app: Flask):
    """
    Drop all tables and recreate them (clears all data).
    
    Args:
        app: Flask application instance
    """
    with app.app_context():
        print("🗑️  Dropping all tables...")
        db.drop_all()
        print("✅ Tables dropped")
        print("🔨 Creating tables...")
        db.create_all()
        print("✅ Database reset complete - all tables recreated")


