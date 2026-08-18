#!/usr/bin/env python3
"""
Database Setup Script for Friday AI Assistant.
- Checks database connectivity.
- Creates required schemas ('chat_schema').
- Creates all database tables and indexes.
"""

import sys
import os

# Ensure the root project directory is in the python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from sqlalchemy import create_engine, text, inspect
from app.core.config import settings
from app.core.logger import logger
from app.models import Base

def setup_database() -> bool:
    logger.info("=" * 60)
    logger.info("🔧 Starting Friday AI Assistant Database Setup...")
    logger.info(f"Target Database URL: {settings.PRIMARY_DB.split('@')[-1] if '@' in settings.PRIMARY_DB else settings.PRIMARY_DB}")
    logger.info("=" * 60)

    # Step 1: Initialize Engine & Check Connection
    logger.info("📡 Step 1/3: Checking database connection...")
    try:
        engine = create_engine(
            settings.PRIMARY_DB,
            pool_pre_ping=True,
            connect_args={"connect_timeout": 5}
        )
        with engine.connect() as conn:
            result = conn.execute(text("SELECT 1")).scalar()
            if result != 1:
                raise ValueError("Database test query did not return expected result.")
        logger.info("✅ Database connection verified successfully!")
    except Exception as e:
        logger.error(f"❌ Database connection failed: {e}")
        logger.error("Please verify that PostgreSQL is running and the credentials in .env are correct.")
        return False

    # Step 2: Create Schema
    logger.info("📁 Step 2/3: Creating database schema ('chat_schema')...")
    try:
        with engine.begin() as conn:
            conn.execute(text("CREATE SCHEMA IF NOT EXISTS chat_schema;"))
        logger.info("✅ Schema 'chat_schema' is ready.")
    except Exception as e:
        logger.error(f"❌ Failed to create schema 'chat_schema': {e}")
        return False

    # Step 3: Create Tables & Indexes
    logger.info("🏗️  Step 3/3: Creating tables and indexes...")
    try:
        # Create all tables registered in Base.metadata
        Base.metadata.create_all(bind=engine)
        
        # Ensure partial unique index on primary chat
        with engine.begin() as conn:
            conn.execute(text("""
                CREATE UNIQUE INDEX IF NOT EXISTS ix_unique_primary_chat 
                ON chat_schema.conversations (is_primary_chat) 
                WHERE (is_primary_chat = true);
            """))
            
        # Inspect created tables in chat_schema
        inspector = inspect(engine)
        tables = inspector.get_table_names(schema="chat_schema")
        logger.info(f"✅ Tables created/verified in 'chat_schema': {tables}")
        
    except Exception as e:
        logger.error(f"❌ Failed to create tables or indexes: {e}")
        return False

    logger.info("=" * 60)
    logger.info("🎉 Database setup completed successfully!")
    logger.info("=" * 60)
    return True

if __name__ == "__main__":
    success = setup_database()
    sys.exit(0 if success else 1)
