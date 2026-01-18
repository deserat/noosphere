#!/bin/bash
set -e

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${GREEN}=== Noosphere Database Setup ===${NC}"

# Configuration
DB_NAME="noosphere"
DB_USER="noosphere_user"
DB_PASSWORD="dev_password"
DB_HOST="localhost"
DB_PORT="5432"

# Check if PostgreSQL is running
if ! pg_isready -h $DB_HOST -p $DB_PORT > /dev/null 2>&1; then
    echo -e "${RED}Error: PostgreSQL is not running on $DB_HOST:$DB_PORT${NC}"
    echo "Start PostgreSQL with: brew services start postgresql@16"
    exit 1
fi

# Check if database exists
if psql -U $(whoami) -lqt | cut -d \| -f 1 | grep -qw $DB_NAME; then
    echo -e "${YELLOW}Warning: Database '$DB_NAME' already exists${NC}"
    read -p "Drop and recreate? (y/N) " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        echo "Dropping database '$DB_NAME'..."
        psql -U $(whoami) -c "DROP DATABASE IF EXISTS $DB_NAME;"
    else
        echo "Skipping database creation"
        DB_EXISTS=true
    fi
fi

# Create database
if [ "$DB_EXISTS" != "true" ]; then
    echo "Creating database '$DB_NAME'..."
    psql -U $(whoami) -c "CREATE DATABASE $DB_NAME;"
fi

# Check if user exists
if psql -U $(whoami) -t -c "SELECT 1 FROM pg_roles WHERE rolname='$DB_USER'" | grep -q 1; then
    echo "User '$DB_USER' already exists, skipping creation"
else
    echo "Creating user '$DB_USER'..."
    psql -U $(whoami) -c "CREATE USER $DB_USER WITH PASSWORD '$DB_PASSWORD';"
fi

# Grant privileges
echo "Granting privileges to '$DB_USER'..."
psql -U $(whoami) -c "GRANT ALL PRIVILEGES ON DATABASE $DB_NAME TO $DB_USER;"

# Connect to database and enable pgvector
echo "Enabling pgvector extension..."
psql -U $(whoami) -d $DB_NAME -c "CREATE EXTENSION IF NOT EXISTS vector;"

# Grant schema privileges (required for table creation)
psql -U $(whoami) -d $DB_NAME -c "GRANT ALL ON SCHEMA public TO $DB_USER;"
psql -U $(whoami) -d $DB_NAME -c "GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO $DB_USER;"
psql -U $(whoami) -d $DB_NAME -c "GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO $DB_USER;"

echo -e "${GREEN}✅ Database setup complete!${NC}"
echo ""
echo "Connection details:"
echo "  Host: $DB_HOST"
echo "  Port: $DB_PORT"
echo "  Database: $DB_NAME"
echo "  User: $DB_USER"
echo "  Password: $DB_PASSWORD"
echo ""
echo "Connection string:"
echo "  postgresql://$DB_USER:$DB_PASSWORD@$DB_HOST:$DB_PORT/$DB_NAME"
echo ""
echo "Test connection:"
echo "  psql -U $DB_USER -d $DB_NAME -h $DB_HOST"
