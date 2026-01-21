#!/bin/bash
# Script to build and publish E2B custom template for Code Interpreter
# CRITICAL: Uses -c flag to start Jupyter kernel server

set -e  # Exit on error

echo "🚀 E2B Custom Template Builder"
echo "================================"

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Check if Docker is running
echo -e "${YELLOW}📦 Checking Docker...${NC}"
if ! docker info > /dev/null 2>&1; then
    echo -e "${RED}❌ Docker is not running. Please start Docker and try again.${NC}"
    exit 1
fi
echo -e "${GREEN}✓ Docker is running${NC}"

# Check if E2B CLI is installed
echo -e "${YELLOW}🔧 Checking E2B CLI...${NC}"
if ! command -v e2b &> /dev/null; then
    echo -e "${RED}❌ E2B CLI not found.${NC}"
    echo "Install it with:"
    echo "  npm install -g @e2b/cli"
    echo "or"
    echo "  curl -fsSL https://raw.githubusercontent.com/e2b-dev/e2b/main/install.sh | bash"
    exit 1
fi
echo -e "${GREEN}✓ E2B CLI found${NC}"

# Check if logged in
echo -e "${YELLOW}🔐 Checking E2B authentication...${NC}"
if ! e2b auth status > /dev/null 2>&1; then
    echo -e "${YELLOW}Not logged in. Running e2b auth login...${NC}"
    e2b auth login
fi
echo -e "${GREEN}✓ Authenticated with E2B${NC}"

# Test Dockerfile locally first
echo -e "${YELLOW}🏗️  Testing Dockerfile locally...${NC}"
docker build -t sandbox-system-test:latest .
if [ $? -eq 0 ]; then
    echo -e "${GREEN}✓ Local Docker build successful${NC}"
else
    echo -e "${RED}❌ Docker build failed. Fix Dockerfile errors first.${NC}"
    exit 1
fi

# Test the built image
echo -e "${YELLOW}🧪 Testing built image...${NC}"
docker run --rm sandbox-system:latest python -c "import numpy; print(f'NumPy: {numpy.__version__}')"
echo -e "${GREEN}✓ Image test passed${NC}"

# Ask user if they want to publish
echo ""
echo -e "${YELLOW}Ready to publish to E2B?${NC}"
echo "This will upload your image to E2B's registry."
read -p "Continue? (y/n) " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "Cancelled."
    exit 0
fi

# Build and publish to E2B with start command (CRITICAL!)
echo -e "${YELLOW}📤 Publishing to E2B...${NC}"
echo -e "${YELLOW}   Using start command: /root/.jupyter/start-up.sh${NC}"
e2b template build -c "/root/.jupyter/start-up.sh"

if [ $? -eq 0 ]; then
    echo -e "${GREEN}✓ Template published successfully!${NC}"
    echo ""
    echo "================================================"
    echo "Next steps:"
    echo "1. Copy the template ID from above"
    echo "2. Use it in your code:"
    echo "   from e2b_code_interpreter import Sandbox"
    echo "   sandbox = Sandbox(template='your-template-id')"
    echo "3. Test it: python scripts/custom_template.py"
    echo "================================================"
else
    echo -e "${RED}❌ Failed to publish template${NC}"
    exit 1
fi

# Cleanup test image
echo -e "${YELLOW}🧹 Cleaning up...${NC}"
docker rmi sandbox-system:latest 2>/dev/null || true
echo -e "${GREEN}✓ Done!${NC}"
