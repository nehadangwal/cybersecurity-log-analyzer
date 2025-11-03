#!/bin/bash

echo "🧪 Running Test Suite for Cybersecurity Log Analyzer"
echo "===================================================="
echo ""

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check if we're in the backend directory
if [ ! -f "requirements.txt" ]; then
    echo -e "${RED}❌ Error: Please run this script from the backend directory${NC}"
    exit 1
fi

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo -e "${YELLOW}📦 Creating virtual environment...${NC}"
    python3 -m venv venv
fi

# Activate virtual environment
echo -e "${YELLOW}🔄 Activating virtual environment...${NC}"
source venv/bin/activate

# Install test dependencies
echo -e "${YELLOW}📦 Installing test dependencies...${NC}"
pip install -q -r requirements.txt
pip install -q -r tests/requirements-test.txt

echo ""
echo -e "${GREEN}✅ Setup complete. Running tests...${NC}"
echo ""

# Run tests with coverage
pytest tests/ -v --cov=app --cov-report=html --cov-report=term-missing

TEST_EXIT_CODE=$?

echo ""
echo "===================================================="

if [ $TEST_EXIT_CODE -eq 0 ]; then
    echo -e "${GREEN}✅ All tests passed!${NC}"
    echo ""
    echo "📊 Coverage report generated in: htmlcov/index.html"
    echo ""
    echo "To view coverage report, run:"
    echo "  open htmlcov/index.html  # macOS"
    echo "  xdg-open htmlcov/index.html  # Linux"
    echo "  start htmlcov/index.html  # Windows"
else
    echo -e "${RED}❌ Some tests failed. Please review the output above.${NC}"
fi

echo ""

deactivate
exit $TEST_EXIT_CODE