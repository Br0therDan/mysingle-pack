#!/bin/bash
# Test runner script for mysingle package

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}Running mysingle package tests...${NC}\n"

# Set test environment
export MYSINGLE_AUTH_BYPASS=true
export ENVIRONMENT=development

# Get the script's directory (works even when called from elsewhere)
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# Detect the correct Python executable
if [ -f ".venv/bin/python" ]; then
    PYTHON_EXEC=".venv/bin/python"
elif [ -f "venv/bin/python" ]; then
    PYTHON_EXEC="venv/bin/python"
elif command -v python3 &> /dev/null; then
    PYTHON_EXEC="python3"
else
    echo -e "${RED}✗ Python executable not found!${NC}"
    exit 1
fi

echo -e "${YELLOW}Using Python: $PYTHON_EXEC${NC}"
echo -e "${YELLOW}Working directory: $SCRIPT_DIR${NC}\n"

# Run tests with coverage
echo -e "${YELLOW}Running pytest with coverage...${NC}"
$PYTHON_EXEC -m pytest tests/ \
    -v \
    --cov=src/mysingle \
    --cov-report=term-missing:skip-covered \
    --cov-report=html:htmlcov \
    --cov-report=xml:coverage.xml \
    "$@"

# Check exit code
if [ $? -eq 0 ]; then
    echo -e "\n${GREEN}✓ All tests passed!${NC}"
    echo -e "${YELLOW}Coverage report: file://$SCRIPT_DIR/htmlcov/index.html${NC}"
else
    echo -e "\n${RED}✗ Tests failed!${NC}"
    exit 1
fi
