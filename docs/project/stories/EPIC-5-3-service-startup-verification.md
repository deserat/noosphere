# Service Startup Scripts and End-to-End Verification

**Epic**: Service Scaffolding
**Priority**: P2
**Story Points**: 3

## User Story

As a developer,
I need coordinated startup scripts and end-to-end verification tests,
So that I can easily start the entire system and verify that all Phase 1 components work together correctly.

## Acceptance Criteria

### Coordinated Startup Script
- [ ] Root-level `start.sh` created to launch all services:
  ```bash
  #!/bin/bash
  set -e

  echo "==================================="
  echo "  Starting Noosphere System v0.1.0"
  echo "==================================="

  # Colors for output
  GREEN='\033[0;32m'
  RED='\033[0;31m'
  NC='\033[0m' # No Color

  # Check prerequisites
  echo ""
  echo "Checking prerequisites..."

  # Check PostgreSQL
  if ! pg_isready -q; then
      echo -e "${RED}✗ PostgreSQL is not running${NC}"
      echo "  Start PostgreSQL: sudo systemctl start postgresql"
      exit 1
  fi
  echo -e "${GREEN}✓ PostgreSQL is running${NC}"

  # Check vault directory
  VAULT_PATH=$(grep "path:" api-service/config.yaml | head -1 | awk '{print $2}' | sed "s|~|$HOME|")
  if [ ! -d "$VAULT_PATH" ]; then
      echo -e "${RED}✗ Vault directory not found: $VAULT_PATH${NC}"
      echo "  Create vault: mkdir -p $VAULT_PATH/{Inbox,People,Projects,Ideas,Admin}"
      exit 1
  fi
  echo -e "${GREEN}✓ Vault directory exists${NC}"

  # Check configuration files
  if [ ! -f "api-service/config.yaml" ]; then
      echo -e "${RED}✗ api-service/config.yaml not found${NC}"
      echo "  Create config: cp api-service/config.example.yaml api-service/config.yaml"
      exit 1
  fi
  if [ ! -f "sync-service/config.yaml" ]; then
      echo -e "${RED}✗ sync-service/config.yaml not found${NC}"
      echo "  Create config: cp sync-service/config.example.yaml sync-service/config.yaml"
      exit 1
  fi
  echo -e "${GREEN}✓ Configuration files exist${NC}"

  echo ""
  echo "Starting services..."
  echo ""

  # Start API service in background
  echo "Starting API service..."
  cd api-service
  source venv/bin/activate
  alembic upgrade head > /dev/null 2>&1
  python -m src.main > ../logs/api-service.log 2>&1 &
  API_PID=$!
  cd ..
  echo -e "${GREEN}✓ API service started (PID: $API_PID)${NC}"

  # Wait for API to be ready
  echo "Waiting for API to be ready..."
  for i in {1..30}; do
      if curl -s http://localhost:8000/api/health/live > /dev/null 2>&1; then
          echo -e "${GREEN}✓ API service is ready${NC}"
          break
      fi
      if [ $i -eq 30 ]; then
          echo -e "${RED}✗ API service failed to start${NC}"
          cat logs/api-service.log
          exit 1
      fi
      sleep 1
  done

  # Start sync service in background
  echo "Starting sync service..."
  cd sync-service
  RUST_LOG=info cargo run --release > ../logs/sync-service.log 2>&1 &
  SYNC_PID=$!
  cd ..
  echo -e "${GREEN}✓ Sync service started (PID: $SYNC_PID)${NC}"

  # Save PIDs for stop script
  echo $API_PID > .api.pid
  echo $SYNC_PID > .sync.pid

  echo ""
  echo "==================================="
  echo -e "${GREEN}✓ All services started successfully${NC}"
  echo "==================================="
  echo ""
  echo "API Service:  http://localhost:8000"
  echo "API Docs:     http://localhost:8000/docs"
  echo "API Health:   http://localhost:8000/api/health"
  echo ""
  echo "Logs:"
  echo "  API:   tail -f logs/api-service.log"
  echo "  Sync:  tail -f logs/sync-service.log"
  echo ""
  echo "Stop services: ./stop.sh"
  echo ""
  ```

### Coordinated Stop Script
- [ ] Root-level `stop.sh` created to stop all services:
  ```bash
  #!/bin/bash

  echo "Stopping Noosphere services..."

  # Stop API service
  if [ -f .api.pid ]; then
      API_PID=$(cat .api.pid)
      if kill -0 $API_PID 2>/dev/null; then
          echo "Stopping API service (PID: $API_PID)..."
          kill -TERM $API_PID
          # Wait for graceful shutdown
          for i in {1..10}; do
              if ! kill -0 $API_PID 2>/dev/null; then
                  echo "✓ API service stopped"
                  break
              fi
              sleep 1
          done
          # Force kill if still running
          if kill -0 $API_PID 2>/dev/null; then
              echo "Force stopping API service..."
              kill -9 $API_PID
          fi
      fi
      rm .api.pid
  fi

  # Stop sync service
  if [ -f .sync.pid ]; then
      SYNC_PID=$(cat .sync.pid)
      if kill -0 $SYNC_PID 2>/dev/null; then
          echo "Stopping sync service (PID: $SYNC_PID)..."
          kill -TERM $SYNC_PID
          # Wait for graceful shutdown
          for i in {1..10}; do
              if ! kill -0 $SYNC_PID 2>/dev/null; then
                  echo "✓ Sync service stopped"
                  break
              fi
              sleep 1
          done
          # Force kill if still running
          if kill -0 $SYNC_PID 2>/dev/null; then
              echo "Force stopping sync service..."
              kill -9 $SYNC_PID
          fi
      fi
      rm .sync.pid
  fi

  echo "✓ All services stopped"
  ```

### Status Check Script
- [ ] Root-level `status.sh` created to check service health:
  ```bash
  #!/bin/bash

  GREEN='\033[0;32m'
  RED='\033[0;31m'
  YELLOW='\033[1;33m'
  NC='\033[0m'

  echo "==================================="
  echo "  Noosphere System Status"
  echo "==================================="
  echo ""

  # Check PostgreSQL
  echo -n "PostgreSQL:    "
  if pg_isready -q; then
      echo -e "${GREEN}✓ Running${NC}"
  else
      echo -e "${RED}✗ Not running${NC}"
  fi

  # Check API service
  echo -n "API Service:   "
  if [ -f .api.pid ]; then
      API_PID=$(cat .api.pid)
      if kill -0 $API_PID 2>/dev/null; then
          if curl -s http://localhost:8000/api/health/live > /dev/null 2>&1; then
              echo -e "${GREEN}✓ Running (PID: $API_PID)${NC}"
          else
              echo -e "${YELLOW}⚠ Running but not responding (PID: $API_PID)${NC}"
          fi
      else
          echo -e "${RED}✗ Not running (stale PID file)${NC}"
          rm .api.pid
      fi
  else
      echo -e "${RED}✗ Not running${NC}"
  fi

  # Check sync service
  echo -n "Sync Service:  "
  if [ -f .sync.pid ]; then
      SYNC_PID=$(cat .sync.pid)
      if kill -0 $SYNC_PID 2>/dev/null; then
          echo -e "${GREEN}✓ Running (PID: $SYNC_PID)${NC}"
      else
          echo -e "${RED}✗ Not running (stale PID file)${NC}"
          rm .sync.pid
      fi
  else
      echo -e "${RED}✗ Not running${NC}"
  fi

  echo ""

  # Show API health if available
  if curl -s http://localhost:8000/api/health > /dev/null 2>&1; then
      echo "API Health:"
      curl -s http://localhost:8000/api/health | jq '.'
  fi

  echo ""
  ```

### End-to-End Verification Script
- [ ] `verify-phase1.sh` created to validate Phase 1 completion:
  ```bash
  #!/bin/bash

  GREEN='\033[0;32m'
  RED='\033[0;31m'
  NC='\033[0m'

  PASSED=0
  FAILED=0

  test_result() {
      if [ $1 -eq 0 ]; then
          echo -e "${GREEN}✓ $2${NC}"
          ((PASSED++))
      else
          echo -e "${RED}✗ $2${NC}"
          ((FAILED++))
      fi
  }

  echo "==================================="
  echo "  Phase 1 Verification Tests"
  echo "==================================="
  echo ""

  # 1. Repository Structure
  echo "1. Repository Structure"
  [ -d "api-service" ] && [ -d "sync-service" ] && [ -d "docs" ]
  test_result $? "Directory structure exists"

  # 2. Python Environment
  echo ""
  echo "2. Python Environment"
  [ -f "api-service/venv/bin/activate" ]
  test_result $? "Python virtual environment exists"

  # 3. Rust Environment
  echo ""
  echo "3. Rust Environment"
  [ -f "sync-service/Cargo.toml" ]
  test_result $? "Rust project configured"

  # 4. Database
  echo ""
  echo "4. Database"
  pg_isready -q
  test_result $? "PostgreSQL is running"

  psql -U noosphere_user -d noosphere -c "SELECT 1" > /dev/null 2>&1
  test_result $? "Database connection works"

  psql -U noosphere_user -d noosphere -c "SELECT COUNT(*) FROM pg_tables WHERE schemaname = 'public'" | grep -q "[0-9]"
  test_result $? "Database tables exist"

  # 5. Vault Structure
  echo ""
  echo "5. Vault Structure"
  VAULT_PATH="$HOME/noosphere-vault"
  [ -d "$VAULT_PATH" ]
  test_result $? "Vault directory exists"

  [ -d "$VAULT_PATH/Inbox" ] && [ -d "$VAULT_PATH/People" ] && \
  [ -d "$VAULT_PATH/Projects" ] && [ -d "$VAULT_PATH/Ideas" ] && \
  [ -d "$VAULT_PATH/Admin" ]
  test_result $? "All category folders exist"

  # 6. Configuration
  echo ""
  echo "6. Configuration"
  [ -f "api-service/config.yaml" ]
  test_result $? "API service config exists"

  [ -f "sync-service/config.yaml" ]
  test_result $? "Sync service config exists"

  # 7. API Service
  echo ""
  echo "7. API Service"
  curl -s http://localhost:8000/api/health/live > /dev/null 2>&1
  test_result $? "API service is running"

  curl -s http://localhost:8000/api/health | grep -q "healthy"
  test_result $? "API health check passes"

  curl -s http://localhost:8000/docs > /dev/null 2>&1
  test_result $? "API documentation accessible"

  # 8. Sync Service
  echo ""
  echo "8. Sync Service"
  [ -f ".sync.pid" ] && kill -0 $(cat .sync.pid) 2>/dev/null
  test_result $? "Sync service is running"

  # 9. End-to-End File Sync Test
  echo ""
  echo "9. End-to-End File Sync Test"
  TEST_FILE="$VAULT_PATH/Inbox/phase1-test-$(date +%s).md"
  echo "# Phase 1 Test" > "$TEST_FILE"
  sleep 2  # Wait for debounce + sync

  # Check sync service log for file detection
  grep -q "$(basename $TEST_FILE)" logs/sync-service.log
  test_result $? "File change detected by sync service"

  rm "$TEST_FILE"

  # Summary
  echo ""
  echo "==================================="
  echo "  Test Results"
  echo "==================================="
  echo -e "${GREEN}Passed: $PASSED${NC}"
  echo -e "${RED}Failed: $FAILED${NC}"
  echo ""

  if [ $FAILED -eq 0 ]; then
      echo -e "${GREEN}✓ Phase 1 verification PASSED${NC}"
      echo "All Phase 1 components are working correctly!"
      exit 0
  else
      echo -e "${RED}✗ Phase 1 verification FAILED${NC}"
      echo "Fix the failed tests before proceeding to Phase 2."
      exit 1
  fi
  ```

### Logs Directory
- [ ] Root-level `logs/` directory created:
  ```bash
  mkdir -p logs
  touch logs/.gitkeep
  ```
- [ ] `.gitignore` updated to exclude logs but keep directory:
  ```gitignore
  # Logs
  logs/*.log

  # Keep logs directory
  !logs/.gitkeep
  ```

### Scripts Made Executable
- [ ] All scripts have execute permissions:
  ```bash
  chmod +x start.sh stop.sh status.sh verify-phase1.sh
  ```

### Documentation
- [ ] `docs/getting-started.md` created with quickstart guide:
  - Prerequisites (PostgreSQL, Python, Rust)
  - Initial setup (vault creation, config files)
  - Starting the system (`./start.sh`)
  - Checking status (`./status.sh`)
  - Stopping the system (`./stop.sh`)
  - Verifying installation (`./verify-phase1.sh`)
  - Troubleshooting common issues

## Technical Notes

**Startup Order**:
1. Verify prerequisites (PostgreSQL, vault directory, config files)
2. Start API service (run migrations, start server)
3. Wait for API to be ready (health check)
4. Start sync service (connects to API)
5. Save PIDs for stop script

**PID File Pattern**:
- Save process IDs to `.api.pid` and `.sync.pid`
- Used by stop script for graceful shutdown
- Cleaned up after services stop
- Check if process is still alive before attempting to stop

**Graceful Shutdown**:
- Send SIGTERM for graceful shutdown
- Wait up to 10 seconds for process to exit
- Force kill (SIGKILL) only if necessary
- Clean up PID files after shutdown

**Health Check Retry**:
- Wait up to 30 seconds for API to be ready
- Retry every 1 second
- Show logs if startup fails
- Prevents sync service from starting before API is ready

**Verification Tests**:
- Repository structure
- Development environments (Python, Rust)
- Database (running, connection, tables)
- Vault structure (directory, categories)
- Configuration files
- API service (running, health, docs)
- Sync service (running)
- End-to-end file sync

**Color-Coded Output**:
- Green: Success
- Red: Failure
- Yellow: Warning
- No Color: Normal output

**Log Management**:
- Separate log files per service
- Logs written to `logs/` directory
- Use `tail -f logs/api-service.log` to monitor
- Logs excluded from git but directory kept

## Dependencies

- **Blocks**:
  - None (Phase 1 completion, ready for Phase 2)
- **Blocked By**:
  - EPIC-5-1 (API service needed)
  - EPIC-5-2 (Sync service needed)
- **Related**:
  - All previous stories (verification tests validate everything)

## Verification

### Start System Test
```bash
# Start all services
./start.sh

# Expected output:
# ===================================
#   Starting Noosphere System v0.1.0
# ===================================
#
# Checking prerequisites...
# ✓ PostgreSQL is running
# ✓ Vault directory exists
# ✓ Configuration files exist
#
# Starting services...
#
# Starting API service...
# ✓ API service started (PID: 12345)
# Waiting for API to be ready...
# ✓ API service is ready
# Starting sync service...
# ✓ Sync service started (PID: 12346)
#
# ===================================
# ✓ All services started successfully
# ===================================
#
# API Service:  http://localhost:8000
# API Docs:     http://localhost:8000/docs
# API Health:   http://localhost:8000/api/health
#
# Logs:
#   API:   tail -f logs/api-service.log
#   Sync:  tail -f logs/sync-service.log
#
# Stop services: ./stop.sh
```

### Status Check Test
```bash
./status.sh

# Expected output:
# ===================================
#   Noosphere System Status
# ===================================
#
# PostgreSQL:    ✓ Running
# API Service:   ✓ Running (PID: 12345)
# Sync Service:  ✓ Running (PID: 12346)
#
# API Health:
# {
#   "status": "healthy",
#   "timestamp": "2024-01-15T10:00:00.000000",
#   "database": "connected",
#   "scheduler": "running",
#   "version": "0.1.0"
# }
```

### Stop System Test
```bash
./stop.sh

# Expected output:
# Stopping Noosphere services...
# Stopping API service (PID: 12345)...
# ✓ API service stopped
# Stopping sync service (PID: 12346)...
# ✓ Sync service stopped
# ✓ All services stopped
```

### Phase 1 Verification Test
```bash
# Start services first
./start.sh

# Run verification
./verify-phase1.sh

# Expected output:
# ===================================
#   Phase 1 Verification Tests
# ===================================
#
# 1. Repository Structure
# ✓ Directory structure exists
#
# 2. Python Environment
# ✓ Python virtual environment exists
#
# 3. Rust Environment
# ✓ Rust project configured
#
# 4. Database
# ✓ PostgreSQL is running
# ✓ Database connection works
# ✓ Database tables exist
#
# 5. Vault Structure
# ✓ Vault directory exists
# ✓ All category folders exist
#
# 6. Configuration
# ✓ API service config exists
# ✓ Sync service config exists
#
# 7. API Service
# ✓ API service is running
# ✓ API health check passes
# ✓ API documentation accessible
#
# 8. Sync Service
# ✓ Sync service is running
#
# 9. End-to-End File Sync Test
# ✓ File change detected by sync service
#
# ===================================
#   Test Results
# ===================================
# Passed: 15
# Failed: 0
#
# ✓ Phase 1 verification PASSED
# All Phase 1 components are working correctly!
```

**Completion Criteria**:
- [ ] start.sh script launches all services successfully
- [ ] stop.sh script stops all services gracefully
- [ ] status.sh script shows current system status
- [ ] verify-phase1.sh validates all Phase 1 components
- [ ] All scripts have execute permissions
- [ ] Logs directory created and configured
- [ ] Documentation explains how to use all scripts
- [ ] Services start in correct order (API before sync)
- [ ] Health checks verify services are ready
- [ ] PID files track running processes
- [ ] Graceful shutdown with timeout and force kill fallback
- [ ] Verification test passes (all Phase 1 components working)
