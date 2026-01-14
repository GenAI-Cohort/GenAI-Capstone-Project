#!/usr/bin/env python3
"""
Database Setup Script

This script connects to a PostgreSQL database and executes the database schema
SQL file to set up the initial database structure, including tables, indexes,
sequences, and initial seed data.

Prerequisites:
    - PostgreSQL database server must be running
    - Database credentials must be configured in environment variables:
      - DB_HOST: Database host (default: localhost)
      - DB_NAME: Database name
      - DB_USER: Database username
      - DB_PASSWORD: Database password
    - pgvector extension should be installed (for vector support)

Usage:
    python scripts/setup_database.py

    Or make it executable and run directly:
    chmod +x scripts/setup_database.py
    ./scripts/setup_database.py

Environment Variables:
    The script uses the following environment variables (loaded from .env file):
    - DB_HOST: PostgreSQL host address (default: localhost)
    - DB_NAME: Name of the database to set up
    - DB_USER: PostgreSQL username
    - DB_PASSWORD: PostgreSQL password

What this script does:
    1. Connects to the PostgreSQL database using credentials from environment
    2. Checks if pgvector extension is available (warns if not)
    3. Reads the DatabaseSchma.sql file
    4. Executes the SQL statements to create:
       - Tables: categories, projects, documents, chunks, document_relationships, chunk_references
       - Indexes: Full-text search, vector similarity, and metadata indexes
       - Sequences: For auto-incrementing IDs
       - Initial seed data: Default project and categories
    5. Commits all changes to the database
    6. Verifies the setup by checking if tables were created successfully

Error Handling:
    - Connection errors: Provides helpful error messages
    - SQL execution errors: Rolls back transaction and reports the error
    - Missing files: Reports if SQL file cannot be found
    - Missing extensions: Warns about missing pgvector but continues

Author: GenAI Capstone Project Team
Date: 2026
"""

import sys
import os
from pathlib import Path
import psycopg2
from psycopg2 import sql
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT

# Add parent directory to path to import config modules
script_dir = Path(__file__).parent
project_root = script_dir.parent
sys.path.insert(0, str(project_root))

try:
    from config.db_connection import get_connection
    from config.database import settings
except ImportError as e:
    print(f"❌ Error importing configuration: {e}")
    print("   Make sure you're running this script from the project root directory.")
    sys.exit(1)


def check_pgvector_extension(conn):
    """
    Check if pgvector extension is available and enabled.
    
    Args:
        conn: PostgreSQL connection object
        
    Returns:
        bool: True if extension is available, False otherwise
    """
    try:
        cur = conn.cursor()
        # Check if extension exists
        cur.execute("""
            SELECT EXISTS(
                SELECT 1 FROM pg_available_extensions 
                WHERE name = 'vector'
            );
        """)
        available = cur.fetchone()[0]
        
        if not available:
            print("⚠️  Warning: pgvector extension is not available.")
            print("   Vector similarity search features may not work.")
            print("   Install pgvector extension if you need vector search capabilities.")
            cur.close()
            return False
        
        # Try to enable it if not already enabled
        cur.execute("CREATE EXTENSION IF NOT EXISTS vector;")
        conn.commit()
        
        # Verify it's enabled
        cur.execute("""
            SELECT extversion FROM pg_extension WHERE extname = 'vector';
        """)
        version = cur.fetchone()
        if version:
            print(f"✅ pgvector extension enabled (version: {version[0]})")
        else:
            print("⚠️  Warning: pgvector extension could not be enabled.")
        
        cur.close()
        return True
    except psycopg2.Error as e:
        print(f"⚠️  Warning: Could not check/enable pgvector extension: {e}")
        conn.rollback()
        return False


def read_sql_file(sql_file_path):
    """
    Read SQL file and return its contents.
    
    Args:
        sql_file_path: Path to the SQL file
        
    Returns:
        str: Contents of the SQL file
        
    Raises:
        FileNotFoundError: If the SQL file doesn't exist
        IOError: If the file cannot be read
    """
    if not sql_file_path.exists():
        raise FileNotFoundError(
            f"SQL file not found: {sql_file_path}\n"
            f"   Please ensure DatabaseSchma.sql exists in the scripts directory."
        )
    
    try:
        with open(sql_file_path, 'r', encoding='utf-8') as f:
            return f.read()
    except IOError as e:
        raise IOError(f"Error reading SQL file: {e}")


def execute_sql_statements(conn, sql_content):
    """
    Execute SQL statements from the provided SQL content.
    
    This function first attempts to execute all SQL statements at once.
    If that fails, it falls back to executing statements individually
    for better error reporting.
    
    Args:
        conn: PostgreSQL connection object
        sql_content: String containing SQL statements
        
    Returns:
        tuple: (success: bool, error_message: str or None)
    """
    cur = conn.cursor()
    
    # First, try executing all statements at once (faster)
    try:
        cur.execute(sql_content)
        cur.close()
        return True, None
    except psycopg2.Error:
        # If bulk execution fails, try executing statement by statement
        # This provides better error reporting
        conn.rollback()
        cur.close()
        
        # Fallback: execute statements individually
        return execute_sql_statements_individual(conn, sql_content)


def execute_sql_statements_individual(conn, sql_content):
    """
    Execute SQL statements one by one for better error reporting.
    
    This is a fallback method when bulk execution fails.
    It splits statements by semicolon and executes them individually.
    
    Args:
        conn: PostgreSQL connection object
        sql_content: String containing SQL statements
        
    Returns:
        tuple: (success: bool, error_message: str or None)
    """
    # Use a simple approach: split by semicolon followed by newline
    # This works for most SQL files
    statements = []
    current = []
    
    for line in sql_content.split('\n'):
        stripped = line.strip()
        # Skip empty lines and single-line comments
        if not stripped or (stripped.startswith('--') and not stripped.startswith('---')):
            continue
        
        current.append(line)
        
        # Check if line ends a statement (semicolon at end)
        if stripped.endswith(';'):
            stmt = '\n'.join(current).strip()
            if stmt and not stmt.startswith('--'):
                statements.append(stmt)
            current = []
    
    # Add any remaining statement
    if current:
        stmt = '\n'.join(current).strip()
        if stmt and not stmt.startswith('--'):
            statements.append(stmt)
    
    if not statements:
        return False, "No valid SQL statements found in file"
    
    cur = conn.cursor()
    print(f"   Executing {len(statements)} statements individually...")
    
    for i, statement in enumerate(statements, 1):
        if not statement.strip() or statement.strip().startswith('--'):
            continue
        
        try:
            cur.execute(statement)
            if i % 5 == 0:
                print(f"   Progress: {i}/{len(statements)} statements executed...")
        except psycopg2.Error as e:
            error_msg = f"Error in statement {i}/{len(statements)}: {str(e)}"
            # Show a preview of the problematic statement
            preview = statement[:150].replace('\n', ' ').strip()
            error_msg += f"\n   Statement preview: {preview}..."
            cur.close()
            return False, error_msg
    
    cur.close()
    return True, None


def verify_setup(conn):
    """
    Verify that the database setup was successful by checking if tables exist.
    
    Args:
        conn: PostgreSQL connection object
        
    Returns:
        bool: True if verification passes, False otherwise
    """
    expected_tables = [
        'categories',
        'projects',
        'documents',
        'chunks',
        'document_relationships',
        'chunk_references'
    ]
    
    try:
        cur = conn.cursor()
        cur.execute("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public' 
            AND table_type = 'BASE TABLE'
            ORDER BY table_name;
        """)
        existing_tables = [row[0] for row in cur.fetchall()]
        cur.close()
        
        print("\n📊 Database Verification:")
        print(f"   Found {len(existing_tables)} tables in database")
        
        missing_tables = []
        for table in expected_tables:
            if table in existing_tables:
                print(f"   ✅ {table}")
            else:
                print(f"   ❌ {table} (missing)")
                missing_tables.append(table)
        
        if missing_tables:
            print(f"\n⚠️  Warning: {len(missing_tables)} expected tables are missing.")
            return False
        
        return True
    except psycopg2.Error as e:
        print(f"❌ Error during verification: {e}")
        return False


def main():
    """
    Main function to set up the database schema.
    
    This function orchestrates the entire database setup process:
    1. Validates environment configuration
    2. Connects to the database
    3. Checks for pgvector extension
    4. Reads and executes the SQL schema file
    5. Verifies the setup
    """
    print("=" * 70)
    print("🗄️  Database Setup Script")
    print("=" * 70)
    
    # Validate configuration
    print("\n📋 Configuration Check:")
    if not settings.DB_HOST:
        print("❌ DB_HOST environment variable is not set")
        sys.exit(1)
    if not settings.DB_NAME:
        print("❌ DB_NAME environment variable is not set")
        sys.exit(1)
    if not settings.DB_USER:
        print("❌ DB_USER environment variable is not set")
        sys.exit(1)
#    if not settings.DB_PASSWORD:
#        print("❌ DB_PASSWORD environment variable is not set")
#        sys.exit(1)
    
    print(f"   Host: {settings.DB_HOST}")
    print(f"   Database: {settings.DB_NAME}")
    print(f"   User: {settings.DB_USER}")
    print("   Password: [REDACTED]")
    
    # Get SQL file path
    sql_file_path = script_dir / "DatabaseSchma.sql"
    print(f"\n📄 SQL File: {sql_file_path}")
    
    if not sql_file_path.exists():
        print(f"❌ SQL file not found: {sql_file_path}")
        print("   Please ensure DatabaseSchma.sql exists in the scripts directory.")
        sys.exit(1)
    
    # Connect to database
    print("\n🔌 Connecting to PostgreSQL database...")
    try:
        conn = get_connection()
        print("✅ Successfully connected to database")
        
        # Get database info
        cur = conn.cursor()
        cur.execute("SELECT version(), current_database(), current_user;")
        db_info = cur.fetchone()
        cur.close()
        
        print(f"   PostgreSQL Version: {db_info[0].split(',')[0]}")
        print(f"   Current Database: {db_info[1]}")
        print(f"   Current User: {db_info[2]}")
        
    except psycopg2.OperationalError as e:
        print(f"❌ Failed to connect to database: {e}")
        print("\n💡 Troubleshooting tips:")
        print("   1. Ensure PostgreSQL server is running")
        print("   2. Verify database credentials in .env file")
        print("   3. Check if database exists (create it if needed)")
        print("   4. Verify network connectivity to database host")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Unexpected error connecting to database: {e}")
        sys.exit(1)
    
    try:
        # Check pgvector extension
        print("\n🔍 Checking pgvector extension...")
        check_pgvector_extension(conn)
        
        # Read SQL file
        print("\n📖 Reading SQL schema file...")
        try:
            sql_content = read_sql_file(sql_file_path)
            print(f"✅ SQL file read successfully ({len(sql_content)} characters)")
        except (FileNotFoundError, IOError) as e:
            print(f"❌ {e}")
            conn.close()
            sys.exit(1)
        
        # Execute SQL statements
        print("\n⚙️  Executing database schema setup...")
        success, error_msg = execute_sql_statements(conn, sql_content)
        
        if not success:
            print(f"\n❌ Error executing SQL statements:")
            print(f"   {error_msg}")
            raise psycopg2.Error(f"SQL execution failed: {error_msg}")
        
        print("✅ SQL statements executed successfully")
        
        # Commit changes
        print("\n💾 Committing changes to database...")
        conn.commit()
        print("✅ Changes committed successfully")
        
        # Verify setup
        if verify_setup(conn):
            print("\n✅ Database setup completed successfully!")
        else:
            print("\n⚠️  Database setup completed with warnings.")
            print("   Some tables may be missing. Please review the output above.")
        
    except psycopg2.Error as e:
        print(f"\n❌ Database error: {e}")
        conn.rollback()
        print("   All changes have been rolled back.")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        conn.rollback()
        sys.exit(1)
    finally:
        conn.close()
        print("\n🔌 Database connection closed")
    
    print("\n" + "=" * 70)
    print("✨ Setup complete!")
    print("=" * 70)


if __name__ == "__main__":
    main()
