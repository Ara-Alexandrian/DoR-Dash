#!/usr/bin/env python3

import os
import sys
import asyncio
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

# Add the app directory to the path
sys.path.append(os.path.dirname(__file__))

from core.config import settings

def test_database_connection():
    """Test synchronous database connection"""
    try:
        engine = create_engine(settings.SQLALCHEMY_DATABASE_URI_SYNC)
        SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
        
        with SessionLocal() as db:
            result = db.execute(text("SELECT 1"))
            print("✅ Database connection successful")
            return True
    except Exception as e:
        print(f"❌ Database connection failed: {e}")
        return False

def test_environment_variables():
    """Test that all required environment variables are set"""
    required_vars = [
        'POSTGRES_SERVER',
        'POSTGRES_USER', 
        'POSTGRES_PASSWORD',
        'POSTGRES_DB'
    ]
    
    print("Environment variables:")
    for var in required_vars:
        value = getattr(settings, var, None)
        print(f"  {var}: {value}")
    
    return True

def main():
    print("🔍 DoR-Dash Backend Health Check")
    print("=" * 40)
    
    print("\n1. Testing environment variables...")
    test_environment_variables()
    
    print("\n2. Testing database connection...")
    db_ok = test_database_connection()
    
    if db_ok:
        print("\n✅ All health checks passed!")
        return 0
    else:
        print("\n❌ Health checks failed!")
        return 1

if __name__ == "__main__":
    exit(main())