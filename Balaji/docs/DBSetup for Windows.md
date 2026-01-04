## To install the pgvector extension for PostgreSQL 18 on Windows 11, you must manually compile and install it, as it is not bundled with the standard installer. 
1. Prerequisites
Ensure you have the following installed on your Windows 11 system:
PostgreSQL 18: Installed via the EDB Windows Installer.
Visual Studio: Install the "Desktop development with C++" workload.
Git: Required to clone the pgvector source code. 

2. Build and Install pgvector

# a .Open the x64 Native Tools Command Prompt for VS as an Administrator and run the following commands: 

# b. Set the PostgreSQL path:
cmd
set "PGROOT=C:\Program Files\PostgreSQL\18"
Use code with caution.

# c. Download the source code:
cmd
cd %TEMP%
git clone --branch v0.8.1 https://github.com/pgvector/pgvector.git
cd pgvector
Use code with caution.

# d. Compile and install:
cmd
nmake /F Makefile.win
nmake /F Makefile.win install
Use code with caution.

 
3. Enable the Extension in PostgreSQL 
Once installed, you must enable the extension for each specific database where you want to use it. 
Connect to your database (e.g., using psql or pgAdmin 4).

Run the following SQL command:
sql

CREATE EXTENSION vector;
Use code with caution.

Note: Although common practice refers to it as "pgvector," the internal extension name is simply vector. 

4. Verification

Verify the installation by creating a table with a vector column: 
sql
CREATE TABLE items (id bigserial PRIMARY KEY, embedding vector(3));
-- Check installed extensions
\dx

### Following  section is  to creat Vector extension, table and index in PostgreSQL 18.

CREATE EXTENSION vector;

SELECT * FROM pg_available_extensions WHERE name = 'vector';

CREATE TABLE chunks (
    id BIGSERIAL PRIMARY KEY,
    document_id TEXT NOT NULL,
	chunk_index INTEGER NOT NULL,
	conten TEXT NOT NULL,
	embedding vector(384),-- 384 dimensions for MiniLM
	metadata JSONB,
	create_at TIMESTAMPTZ DEFAULT Now()
);

# --Add indexes
# -- a. Vector similarity search (HNSW -best for large data set)
CREATE INDEX document_chunks_embedding_idx 
on chunks
Using hnsw (embedding vector_cosine_ops);

# -- b. Filter by Document

CREATE INDEX document_chunks_document_id_idx
ON chunks (document_id);