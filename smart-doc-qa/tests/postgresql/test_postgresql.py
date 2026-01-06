#!/usr/bin/env python3
"""
Test PostgreSQL installation and psycopg2-binary connection
"""
import sys

def test_psycopg2_import():
    """Test if psycopg2 can be imported"""
    try:
        import psycopg2
        print(f"✅ psycopg2-binary imported successfully")
        print(f"   Version: {psycopg2.__version__}")
        return True
    except ImportError as e:
        print(f"❌ Failed to import psycopg2: {e}")
        return False

def test_postgresql_connection():
    """Test connection to PostgreSQL"""
    try:
        import psycopg2
        
        # Try to connect to default database
        # On macOS with Homebrew, default user is your system username
        import getpass
        username = getpass.getuser()
        
        print(f"\n🔌 Attempting to connect to PostgreSQL...")
        print(f"   User: {username}")
        print(f"   Database: postgres (default)")
        
        conn = psycopg2.connect(
            host="localhost",
            port=5432,
            user=username,
            database="postgres"
        )
        
        print("✅ Successfully connected to PostgreSQL!")
        
        # Test query
        cur = conn.cursor()
        cur.execute("SELECT version();")
        version = cur.fetchone()[0]
        print(f"\n📊 PostgreSQL Version:")
        print(f"   {version}")
        
        # Get database info
        cur.execute("SELECT current_database(), current_user;")
        db_info = cur.fetchone()
        
        # Test pgvector extension (if needed)
        try:
            cur.execute("SELECT extname, extversion FROM pg_extension WHERE extname = 'vector';")
            vector_ext = cur.fetchone()
            if vector_ext:
                print(f"\n✅ pgvector extension installed")
                print(f"   Version: {vector_ext[1]}")
            else:
                # Try to create it
                cur.execute("CREATE EXTENSION IF NOT EXISTS vector;")
                conn.commit()
                cur.execute("SELECT extversion FROM pg_extension WHERE extname = 'vector';")
                version = cur.fetchone()[0]
                print(f"\n✅ pgvector extension created")
                print(f"   Version: {version}")
        except Exception as e:
            print(f"\n⚠️  pgvector extension not available: {e}")
            print("   (This is optional - install separately if needed)")
            conn.rollback()  # Rollback the failed transaction
        print(f"\n📋 Connection Info:")
        print(f"   Database: {db_info[0]}")
        print(f"   User: {db_info[1]}")
        
        cur.close()
        conn.close()
        print("\n✅ All tests passed! PostgreSQL is working correctly.")
        return True
        
    except psycopg2.OperationalError as e:
        print(f"\n❌ Connection failed: {e}")
        print("\n💡 Troubleshooting:")
        print("   1. Make sure PostgreSQL is running: brew services start postgresql@15")
        print("   2. Check if default database exists")
        print("   3. Verify user permissions")
        return False
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        return False

def main():
    print("=" * 60)
    print("PostgreSQL Installation Test")
    print("=" * 60)
    
    # Test import
    if not test_psycopg2_import():
        sys.exit(1)
    
    # Test connection
    if not test_postgresql_connection():
        sys.exit(1)
    
    print("\n" + "=" * 60)
    print("✅ All tests passed!")
    print("=" * 60)

if __name__ == "__main__":
    main()

