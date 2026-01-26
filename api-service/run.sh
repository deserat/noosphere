#!/bin/bash
set -e  # Exit on error

# Noosphere API Service Startup Script
# Loads environment, runs migrations, and starts the FastAPI server

# Script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "  Noosphere API Service Startup"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo

# Load environment variables
if [ -f .env ]; then
    echo "✓ Loading environment variables from .env..."
    set -a  # Automatically export all variables
    source .env
    set +a  # Disable auto-export
else
    echo "⚠ Warning: .env file not found. Using system environment variables only."
fi

# Check config.yaml exists
if [ ! -f config.yaml ]; then
    echo "✗ Error: config.yaml not found"
    echo "Hint: Copy config.example.yaml to config.yaml and customize"
    exit 1
fi
echo "✓ Configuration file found: config.yaml"

# Run database migrations
echo
echo "Running database migrations..."
uv run alembic upgrade head
echo "✓ Database migrations complete"

# Read config values (with defaults)
HOST="${API_HOST:-127.0.0.1}"
PORT="${API_PORT:-8000}"
DEBUG="${API_DEBUG:-false}"

echo
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "  Starting API server"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "  Host:  $HOST"
echo "  Port:  $PORT"
echo "  Debug: $DEBUG"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo

# Start server
if [ "$DEBUG" = "true" ]; then
    # Development mode with auto-reload
    echo "Starting in DEVELOPMENT mode (auto-reload enabled)..."
    uv run uvicorn app.main:app --reload --host "$HOST" --port "$PORT"
else
    # Production mode
    echo "Starting in PRODUCTION mode..."
    uv run uvicorn app.main:app --host "$HOST" --port "$PORT"
fi
