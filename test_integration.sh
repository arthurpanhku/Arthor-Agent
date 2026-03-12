#!/bin/bash
set -e

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${BLUE}=== DocSentinel Integration Test Suite ===${NC}"

# 1. Environment Check
echo -e "${BLUE}[1/3] Checking Environment...${NC}"
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}Error: python3 could not be found.${NC}"
    exit 1
fi

# Create venv if not exists
if [ ! -d ".venv_test" ]; then
    echo "  > Creating test virtual environment (.venv_test)..."
    python3 -m venv .venv_test
fi

source .venv_test/bin/activate

# 2. Dependencies
echo -e "${BLUE}[2/3] Installing Dependencies...${NC}"
pip install -q --upgrade pip
if [ -f "requirements.txt" ]; then
    pip install -q -r requirements.txt
fi
if [ -f "requirements-dev.txt" ]; then
    pip install -q -r requirements-dev.txt
fi
echo "  > Dependencies installed."

# 3. Run Tests
echo -e "${BLUE}[3/3] Running Tests (pytest)...${NC}"

# Run unit and integration tests
# We skip 'test_deployment' if it exists, as that might require docker
# But we run everything else
pytest tests/ -v --durations=5

TEST_EXIT_CODE=$?

if [ $TEST_EXIT_CODE -eq 0 ]; then
    echo -e "${GREEN}=== All Tests Passed! ===${NC}"
    # Optional: Run simple health check if service is running locally
    if curl -s http://localhost:8000/health > /dev/null; then
        echo -e "${GREEN}  > Local API is reachable.${NC}"
    fi
    exit 0
else
    echo -e "${RED}=== Tests Failed! (Exit Code: $TEST_EXIT_CODE) ===${NC}"
    exit $TEST_EXIT_CODE
fi
