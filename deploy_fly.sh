#!/bin/bash
# deploy_fly.sh - Secure & Fixed

set -e

echo "🚀 Starting Deployment Process..."

# 1. Check for flyctl
if ! command -v flyctl &> /dev/null; then
    echo "❌ flyctl not found. Install it first."
    exit 1
fi

# 2. Authentication Check
echo "🔍 Checking Auth..."
if ! flyctl auth whoami > /dev/null 2>&1; then
    echo "⚠️ Not logged in. Logging in..."
    flyctl auth login
fi

# 3. Import Secrets Securely (Supports spaces and special chars)
echo "🔐 Importing secrets from .env..."
if [ -f .env ]; then
    # This method is safer than xargs for values with spaces
    cat .env | flyctl secrets import
else
    echo "⚠️ .env file not found! Skipping secrets."
fi

# 4. Deploy
echo "🚀 Deploying to Fly.io..."
flyctl deploy --remote-only

echo "✅ Deployment completed!"
