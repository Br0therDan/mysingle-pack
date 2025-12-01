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

# Run tests with coverage
echo -e "${YELLOW}Running pytest with coverage...${NC}"
uv run python -m pytest tests/ \
    -v \
    --cov=mysingle \
    --cov-report=term-missing \
    --cov-report=html \
    --cov-report=xml \
    "$@"

# Check exit code
if [ $? -eq 0 ]; then
    echo -e "\n${GREEN}✓ All tests passed!${NC}"
    echo -e "${YELLOW}Coverage report generated in htmlcov/index.html${NC}"
else
    echo -e "\n${RED}✗ Tests failed!${NC}"
    exit 1
fi
