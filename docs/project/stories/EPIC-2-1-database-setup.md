# PostgreSQL with pgvector Installation and Configuration

**Epic**: Database Foundation
**Priority**: P0
**Story Points**: 5

## User Story

Implement PostgreSQL database with pgvector extension for the Noosphere system to provide persistent storage and AI-ready vector search capabilities.

## Acceptance Criteria

### PostgreSQL Installation
- [ ] PostgreSQL 14+ installed locally:
  ```bash
  # Ubuntu/Debian
  sudo apt-get install postgresql-14

  # macOS
  brew install postgresql@14

  # Verify installation
  psql --version  # Should show 14.x or higher
  ```
- [ ] PostgreSQL service running:
  ```bash
  sudo systemctl status postgresql  # Linux
  brew services list | grep postgresql  # macOS
  ```
- [ ] PostgreSQL accessible via psql client

### pgvector Extension Setup
- [ ] pgvector extension installed:
  ```bash
  # Ubuntu/Debian
  sudo apt-get install postgresql-14-pgvector

  # macOS
  brew install pgvector

  # Or build from source if not available in package manager
  ```
- [ ] pgvector extension verified in PostgreSQL:
  ```sql
  CREATE EXTENSION IF NOT EXISTS vector;
  SELECT * FROM pg_extension WHERE extname = 'vector';
  ```

### Database and User Creation
- [ ] Noosphere database created:
  ```bash
  sudo -u postgres createdb noosphere
  ```
- [ ] Database user created with appropriate permissions:
  ```sql
  CREATE USER noosphere_user WITH PASSWORD 'dev_password';
  GRANT ALL PRIVILEGES ON DATABASE noosphere TO noosphere_user;

  -- Grant schema permissions
  \c noosphere
  GRANT ALL ON SCHEMA public TO noosphere_user;
  GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO noosphere_user;
  GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO noosphere_user;
  ```
- [ ] User can connect to database:
  ```bash
  psql -U noosphere_user -d noosphere -h localhost
  ```

### Connection Configuration
- [ ] Connection string format documented in `.env.example`:
  ```bash
  DATABASE_URL=postgresql://noosphere_user:dev_password@localhost:5432/noosphere
  ```
- [ ] Connection parameters documented:
  - Host: localhost (for local development)
  - Port: 5432 (default PostgreSQL port)
  - Database: noosphere
  - User: noosphere_user
  - Password: Stored in .env file (never committed)
- [ ] Production connection security notes documented:
  - Use environment variables for credentials
  - Never commit passwords to git
  - Use connection pooling (to be implemented in database connection module)
  - Consider SSL/TLS for production deployments

### Documentation
- [ ] Database setup instructions added to `docs/setup.md`:
  - Platform-specific installation commands
  - pgvector installation steps
  - Database and user creation
  - Troubleshooting common issues
- [ ] Database architecture documented in `docs/database.md`:
  - Why PostgreSQL (ACID compliance, reliability, pgvector support)
  - Why pgvector (semantic search for AI features)
  - Schema will be defined in models (see EPIC-2-2)
  - Migration strategy (Alembic)

## Technical Notes

**PostgreSQL Version Selection**:
- **Minimum**: PostgreSQL 14 (better JSON support, performance improvements)
- **Recommended**: PostgreSQL 15+ (if available)
- **pgvector**: Requires PostgreSQL 11+ but works best with 14+

**pgvector Extension**:
- Enables vector similarity search using cosine distance, L2 distance, inner product
- Critical for semantic search features (AI embeddings)
- Column type: `vector(n)` where n = embedding dimension (e.g., 1536 for OpenAI)
- Indexes: ivfflat or hnsw for fast approximate nearest neighbor search

**Security Considerations**:
- **Development**: Simple password OK, database on localhost
- **Production**:
  - Strong passwords
  - Connection pooling with max connection limits
  - SSL/TLS encryption
  - Principle of least privilege (separate read-only users if needed)
  - Consider using managed PostgreSQL (Cloud SQL, RDS, Supabase)

**Common Issues and Solutions**:
1. **PostgreSQL not starting**: Check port 5432 not in use, check logs
2. **pgvector not found**: Ensure extension installed for correct PG version
3. **Permission denied**: Check user has GRANT ALL on database
4. **Connection refused**: Check PostgreSQL listening on correct host/port

**Alternative Installation Methods**:
- Docker: `docker run -d -p 5432:5432 -e POSTGRES_PASSWORD=dev_password ankane/pgvector`
- This can simplify setup but adds Docker dependency

## Dependencies

- **Blocks**:
  - EPIC-2-2 (Database models need database to exist)
  - EPIC-2-3 (Database connection needs database configured)
  - EPIC-5-1 (API service needs database for health check)
- **Blocked By**:
  - EPIC-1-1 (Repository structure needed for migrations directory)
- **Related**:
  - EPIC-1-2 (Python environment needed for psycopg2 client)

## Verification

### Installation Verification
```bash
# Check PostgreSQL version
psql --version
# Expected: psql (PostgreSQL) 14.x or higher

# Check PostgreSQL is running
sudo systemctl status postgresql  # Linux
brew services list | grep postgresql  # macOS
# Expected: active (running)

# Check pgvector extension available
sudo -u postgres psql -c "SELECT * FROM pg_available_extensions WHERE name = 'vector';"
# Expected: Row showing vector extension
```

### Database Access Verification
```bash
# Connect as postgres user
sudo -u postgres psql

# Inside psql:
\l  # List databases - should show 'noosphere'
\du  # List users - should show 'noosphere_user'

# Connect as noosphere_user
psql -U noosphere_user -d noosphere -h localhost

# Inside psql as noosphere_user:
\dx  # List extensions - should show 'vector' if enabled
CREATE TABLE test_vector (id serial PRIMARY KEY, embedding vector(3));
INSERT INTO test_vector (embedding) VALUES ('[1,2,3]');
SELECT * FROM test_vector;
DROP TABLE test_vector;
\q
```

### Python Connection Test
```bash
cd api-service
source venv/bin/activate

# Test connection with psycopg2
python -c "
import psycopg2
from psycopg2 import sql

conn = psycopg2.connect(
    dbname='noosphere',
    user='noosphere_user',
    password='dev_password',
    host='localhost',
    port='5432'
)
cur = conn.cursor()
cur.execute('SELECT version();')
print(cur.fetchone())
cur.close()
conn.close()
print('✓ Database connection successful')
"
```

**Completion Criteria**:
- [ ] PostgreSQL 14+ running and accessible
- [ ] pgvector extension installed and verified
- [ ] noosphere database exists
- [ ] noosphere_user can connect and create tables
- [ ] Connection string documented and tested
- [ ] Setup instructions allow a new developer to reproduce environment
- [ ] Python can connect to database using psycopg2
