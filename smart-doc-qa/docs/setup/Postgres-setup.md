```markdown
# Homebrew PostgreSQL 14 + pgvector Installation Guide
*For VS Code Markdown Preview / Notes*

## 🛠️ Prerequisites
- macOS (Apple Silicon or Intel)
- Terminal access
- Admin privileges (`sudo`)

## 📦 Step 1: Install Homebrew
```
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
```
[Homebrew Formulae][web:94]

## 🔧 Step 2: Homebrew PATH Setup (Apple Silicon)
```
echo 'eval "$(/opt/homebrew/bin/brew shellenv)"' >> ~/.zprofile
eval "$(/opt/homebrew/bin/brew shellenv)"
exec zsh -l
```

**Intel Macs**: Use `/usr/local` instead of `/opt/homebrew`

## 🐘 Step 3: Install PostgreSQL 14
```
brew install postgresql@14
brew services start postgresql@14
```

## 🌐 Step 4: PostgreSQL PATH
```
echo 'export PATH="/opt/homebrew/opt/postgresql@14/bin:$PATH"' >> ~/.zshrc
exec zsh -l
```

## ✅ Step 5: Verify PostgreSQL 14
```
# Client version
psql --version
# Expected: psql (PostgreSQL) 14.x (Homebrew)

# Server version  
psql postgres -c "SELECT version();"
# Expected: PostgreSQL 14.x

# Services status
brew services list | grep postgresql
```

## 🔗 Step 6: Install pgvector
```
brew install pgvector
brew services restart postgresql@14
```

**Alternative (Source Build)**:
```
cd /tmp
git clone --depth 1 https://github.com/pgvector/pgvector.git
cd pgvector
make PG_CONFIG=/opt/homebrew/opt/postgresql@14/bin/pg_config
sudo make PG_CONFIG=/opt/homebrew/opt/postgresql@14/bin/pg_config install
brew services restart postgresql@14
```
[pgvector GitHub][web:63]

## 🚀 Step 7: Enable pgvector Extension
```
psql postgres -c "CREATE EXTENSION IF NOT EXISTS vector;"
psql postgres -c "\dx"
```
**Expected**: `vector` listed in extensions.

## 📁 Step 8: Verify Files
```
ls /opt/homebrew/share/postgresql@14/extension/vector.control
ls /opt/homebrew/lib/postgresql@14/vector.so
```

## 🧪 Test Table + Index
```
CREATE TABLE documents (
  id bigserial PRIMARY KEY,
  filename text,
  content text,
  chunk text,
  embedding vector(384)  -- 384 dimensions for MiniLM
);

-- HNSW index for fast similarity search
CREATE INDEX ON documents USING hnsw (embedding vector_cosine_ops);


INSERT INTO documents (embedding) VALUES ('[0.1,0.2,0.3]'::vector);
SELECT * FROM documents ORDER BY embedding <-> '[0.1,0.2,0.3]'::vector;
```

## 🔧 Troubleshooting

| Error | Fix |
|-------|-----|
| `psql: command not found` | Step 4 (PATH) |
| `extension "vector" not available` | Step 6 + restart service |
| Multiple PostgreSQL versions | `brew services stop postgresql`<br>`sudo pkill -f postgres`<br>`brew services start postgresql@14` |
| Port 5432 conflict | `lsof -i :5432`<br>`sudo kill <PID>` |

## 📚 References
- [Homebrew PostgreSQL@14][web:94]
- [pgvector][web:63] 
- [Homebrew pgvector][web:110]

---
*Copy this to `postgres-setup.md` in VS Code for reference*
```

**Save as `postgres-setup.md`** in your VS Code workspace. Use **Ctrl+Shift+V** (Mac: Cmd+Shift+V) for Markdown preview with copyable code blocks.[1][2][3]

[1](https://formulae.brew.sh/formula/postgresql@14)
[2](https://github.com/pgvector/pgvector)
[3](https://formulae.brew.sh/formula/pgvector)