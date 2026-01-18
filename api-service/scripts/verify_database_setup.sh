#!/bin/bash

GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo -e "${YELLOW}=== Database Setup Verification ===${NC}\n"

FAILURES=0

# Test 1: PostgreSQL running
echo -n "1. PostgreSQL running... "
if pg_isready -h localhost -p 5432 > /dev/null 2>&1; then
    echo -e "${GREEN}✓${NC}"
else
    echo -e "${RED}✗${NC}"
    FAILURES=$((FAILURES + 1))
fi

# Test 2: Database exists
echo -n "2. Database 'noosphere' exists... "
if psql -U $(whoami) -lqt | cut -d \| -f 1 | grep -qw noosphere; then
    echo -e "${GREEN}✓${NC}"
else
    echo -e "${RED}✗${NC}"
    FAILURES=$((FAILURES + 1))
fi

# Test 3: User exists
echo -n "3. User 'noosphere_user' exists... "
if psql -U $(whoami) -t -c "SELECT 1 FROM pg_roles WHERE rolname='noosphere_user'" | grep -q 1; then
    echo -e "${GREEN}✓${NC}"
else
    echo -e "${RED}✗${NC}"
    FAILURES=$((FAILURES + 1))
fi

# Test 4: pgvector extension enabled
echo -n "4. pgvector extension enabled... "
if psql -U $(whoami) -d noosphere -t -c "SELECT 1 FROM pg_extension WHERE extname='vector'" | grep -q 1; then
    echo -e "${GREEN}✓${NC}"
else
    echo -e "${RED}✗${NC}"
    FAILURES=$((FAILURES + 1))
fi

# Test 5: User can connect
echo -n "5. User can connect to database... "
if PGPASSWORD=dev_password psql -U noosphere_user -d noosphere -h localhost -c "SELECT 1" > /dev/null 2>&1; then
    echo -e "${GREEN}✓${NC}"
else
    echo -e "${RED}✗${NC}"
    FAILURES=$((FAILURES + 1))
fi

# Test 6: Alembic initialized
echo -n "6. Alembic initialized... "
if [ -f "alembic.ini" ] && [ -d "alembic" ]; then
    echo -e "${GREEN}✓${NC}"
else
    echo -e "${RED}✗${NC}"
    FAILURES=$((FAILURES + 1))
fi

# Test 7: .env file exists
echo -n "7. .env file exists... "
if [ -f ".env" ]; then
    echo -e "${GREEN}✓${NC}"
else
    echo -e "${RED}✗${NC}"
    FAILURES=$((FAILURES + 1))
fi

echo ""
if [ $FAILURES -eq 0 ]; then
    echo -e "${GREEN}✅ All verification checks passed!${NC}"
    exit 0
else
    echo -e "${RED}✗ $FAILURES check(s) failed${NC}"
    exit 1
fi
