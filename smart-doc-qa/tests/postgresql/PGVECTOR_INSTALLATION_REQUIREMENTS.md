# pgvector Installation Requirements Analysis

## Current Status

### ✅ Already Installed/Configured

1. **PostgreSQL**: ✅ Installed (PostgreSQL 15.15 via Homebrew)
   - Location: `/opt/homebrew/opt/postgresql@15`
   - Status: Running and accessible

2. **Python pgvector package**: ✅ Installed (v0.2.4)
   - Location: In `smart-doc-qa/venv`
   - Status: Python package available for use

3. **PostgreSQL development files**: ✅ Available
   - `pg_config` available at: `/opt/homebrew/opt/postgresql@15/bin/pg_config`
   - Development headers and libraries present

### ❌ Missing Components

1. **PostgreSQL pgvector extension**: ❌ NOT INSTALLED
   - Extension files not found in: `/opt/homebrew/opt/postgresql@15/share/postgresql@15/extension/`
   - Shared library not found in: `/opt/homebrew/opt/postgresql@15/lib/postgresql/`
   - Status: Extension cannot be created in database

## Installation Challenge

### Issue: PostgreSQL Version Mismatch

- **Your PostgreSQL version**: 15.15
- **Homebrew pgvector formula requirement**: PostgreSQL 17 or 18
- **Result**: Cannot use `brew install pgvector` directly

### Solution Options

#### Option 1: Compile from Source (Recommended for PostgreSQL 15)

**What's needed:**

1. ✅ Build tools (make, gcc/clang) - Available on macOS
2. ✅ PostgreSQL development files - Already installed
3. ✅ Git - For cloning pgvector repository
4. ❌ pgvector source code - Need to clone from GitHub
5. ❌ Compiled extension files - Need to build and install

**Steps required:**

```bash
# 1. Clone pgvector repository
git clone --branch v0.8.1 https://github.com/pgvector/pgvector.git
cd pgvector

# 2. Set PostgreSQL paths
export PATH="/opt/homebrew/opt/postgresql@15/bin:$PATH"
export LDFLAGS="-L/opt/homebrew/opt/postgresql@15/lib"
export CPPFLAGS="-I/opt/homebrew/opt/postgresql@15/include"

# 3. Build and install
make
sudo make install

# 4. Enable in database
psql -U balaji -d postgres -c "CREATE EXTENSION vector;"
```

#### Option 2: Upgrade PostgreSQL (Alternative)

**What's needed:**

1. ❌ Upgrade PostgreSQL from 15 to 17 or 18
2. ❌ Migrate existing databases (if any)
3. ✅ Then use: `brew install pgvector`

**Note**: This is more disruptive and may require database migration.

## Summary of Missing Items

### System Level (PostgreSQL Extension)

- ❌ **pgvector extension files** - Need to compile from source
- ❌ **pgvector shared library** (`vector.so`) - Need to compile from source
- ❌ **Extension control file** (`vector.control`) - Need to compile from source
- ❌ **Extension SQL files** (`vector--*.sql`) - Need to compile from source

### Python Level

- ✅ **pgvector Python package** (v0.2.4) - Already installed
- ✅ **psycopg2-binary** (v2.9.11) - Already installed

### Build Tools

- ✅ **make** - Available on macOS
- ✅ **C compiler** (clang/gcc) - Available on macOS
- ✅ **Git** - Available on macOS
- ✅ **PostgreSQL development files** - Already installed

## What Needs to Be Done

1. **Clone pgvector source code** from GitHub
2. **Compile the extension** using make
3. **Install the extension** into PostgreSQL 15
4. **Enable the extension** in your database(s)

## Verification Commands

After installation, verify with:

```bash
# Check extension files exist
ls /opt/homebrew/opt/postgresql@15/share/postgresql@15/extension/vector*

# Check shared library exists
ls /opt/homebrew/opt/postgresql@15/lib/postgresql/vector.so

# Test in database
psql -U balaji -d postgres -c "CREATE EXTENSION vector;"
psql -U balaji -d postgres -c "SELECT * FROM pg_available_extensions WHERE name = 'vector';"
```

## Notes

- The Python `pgvector` package (v0.2.4) is just a client library for working with vector types
- The PostgreSQL extension must be installed separately at the database level
- PostgreSQL 15 is supported by pgvector, but requires compilation from source
- The extension needs to be enabled in each database where you want to use it
