from .database import db
from .models import *
import os

def init_database():
    """Initialize database with all tables"""
    try:
        db.create_all()
        print("✅ Database initialized successfully!")
        print(f"   Created tables: {', '.join(db.metadata.tables.keys())}")
        return True
    except Exception as e:
        print(f"❌ Error initializing database: {e}")
        return False

def drop_database():
    """Drop all tables"""
    try:
        db.drop_all()
        print("✅ Database dropped successfully!")
        return True
    except Exception as e:
        print(f"❌ Error dropping database: {e}")
        return False

def reset_database():
    """Reset database (drop and recreate)"""
    if drop_database():
        return init_database()
    return False

def check_database():
    """Check if database exists and has tables"""
    try:
        # Check if any table exists
        tables = db.metadata.tables.keys()
        if tables:
            print(f"✅ Database exists with tables: {', '.join(tables)}")
            return True
        else:
            print("⚠️ Database exists but no tables found")
            return False
    except Exception as e:
        print(f"❌ Error checking database: {e}")
        return False