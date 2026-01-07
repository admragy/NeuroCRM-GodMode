#!/bin/bash
# ==============================================
# OmniCRM God Mode - Fly.io Deployment Script
# ==============================================

set -e  # Exit on any error

echo "🚀 Starting OmniCRM God Mode Deployment to Fly.io..."
echo ""

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check if flyctl is installed
if ! command -v flyctl &> /dev/null; then
    echo -e "${RED}❌ flyctl not found!${NC}"
    echo ""
    echo "Please install flyctl first:"
    echo "  curl -L https://fly.io/install.sh | sh"
    echo ""
    echo "Then add it to your PATH:"
    echo "  export PATH=\"\$HOME/.fly/bin:\$PATH\""
    exit 1
fi

echo -e "${GREEN}✅ flyctl found${NC}"

# Check authentication
echo ""
echo "🔍 Checking Fly.io authentication..."
if ! flyctl auth whoami > /dev/null 2>&1; then
    echo -e "${YELLOW}⚠️  Not logged in to Fly.io${NC}"
    echo ""
    echo "Logging in..."
    flyctl auth login
    echo ""
fi

echo -e "${GREEN}✅ Authenticated${NC}"

# Check if .env file exists
if [ -f .env ]; then
    echo ""
    echo "🔐 Importing secrets from .env..."
    cat .env | flyctl secrets import --app neurocrm-godmode-v1
    echo -e "${GREEN}✅ Secrets imported${NC}"
else
    echo ""
    echo -e "${YELLOW}⚠️  No .env file found${NC}"
    echo "Skipping secrets import"
    echo ""
    echo "To add secrets later, run:"
    echo "  cat .env | flyctl secrets import --app neurocrm-godmode-v1"
fi

# Deploy
echo ""
echo "🚀 Deploying to Fly.io..."
echo ""
flyctl deploy --remote-only --app neurocrm-godmode-v1

echo ""
echo -e "${GREEN}✅ Deployment completed!${NC}"
echo ""
echo "📊 Checking deployment status..."
flyctl status --app neurocrm-godmode-v1

echo ""
echo "🌐 Your app is live at:"
echo "   https://neurocrm-godmode-v1.fly.dev"
echo ""
echo "📝 Useful commands:"
echo "   flyctl logs --app neurocrm-godmode-v1           # View logs"
echo "   flyctl status --app neurocrm-godmode-v1         # Check status"
echo "   flyctl ssh console --app neurocrm-godmode-v1    # SSH into app"
echo "   flyctl scale show --app neurocrm-godmode-v1     # View scaling"
echo ""
echo -e "${GREEN}🎉 Done!${NC}"
