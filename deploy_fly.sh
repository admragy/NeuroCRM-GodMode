#!/bin/bash
set -e

echo "✈️  OmniCRM Ultimate - Fly.io Deployment"
echo "=========================================="

FLY_API_TOKEN="fm2_lJPECAAAAAAAC2d9xBAhDgb23qDOFrO23eHh8/K8wrVodHRwczovL2FwaS5mbHkuaW8vdjGWAJLOABTivx8Lk7lodHRwczovL2FwaS5mbHkuaW8vYWFhL3YxxDyGVM6iupXOZnkW3wiLjNWqzsO4/EyIBQ3Ni6R2JS3lgJcUaZ3k/nBeXIRKnGeXNYMmScDcOLAtbKP/2bTETkks4fgTdC+mB3xzwFpUn7AimbaU69xNlUEG6OLmCX8UiPQQ82JSWhVS9fgEiPb/rFqmd+bIci57hDM1vlAPnKqcLhMUWIjcKBFie77TKg2SlAORgc4Av3nlHwWRgqdidWlsZGVyH6J3Zx8BxCAhyh2w3sD3hbQIjJIKKizjp3fMJacrNYe7EjFGpuy7Qw=="
export FLY_API_TOKEN

# Check if flyctl is installed
if ! command -v flyctl &> /dev/null; then
    echo "📥 Installing flyctl..."
    curl -L https://fly.io/install.sh | sh
    export FLYCTL_INSTALL="/home/user/.fly"
    export PATH="$FLYCTL_INSTALL/bin:$PATH"
fi

echo "✅ flyctl found"

# Authenticate
echo "🔐 Authenticating with Fly.io..."
flyctl auth token $FLY_API_TOKEN

# Check if app exists
echo "🔍 Checking if app exists..."
if flyctl apps list | grep -q "omnicrm-ultimate"; then
    echo "✅ App exists, deploying update..."
    flyctl deploy --remote-only --ha=false
else
    echo "📦 Creating new app..."
    flyctl launch --name omnicrm-ultimate --region fra --no-deploy --copy-config
    
    # Set secrets
    echo "🔐 Setting secrets..."
    flyctl secrets set \
        ENVIRONMENT=production \
        DEBUG=False \
        SECRET_KEY="$(openssl rand -base64 64 | tr -d '\n')" \
        JWT_SECRET_KEY="$(openssl rand -base64 64 | tr -d '\n')" \
        ENCRYPTION_KEY="$(openssl rand -base64 32 | tr -d '\n')" \
        AES_KEY="$(openssl rand -base64 32 | tr -d '\n')"
    
    # Deploy
    echo "🚀 Deploying..."
    flyctl deploy --remote-only --ha=false
fi

# Get app info
echo ""
echo "================================================"
echo "✅ DEPLOYMENT COMPLETE!"
echo "================================================"
echo ""
flyctl info
echo ""
echo "🌐 App URL: https://omnicrm-ultimate.fly.dev"
echo "📊 Dashboard: https://fly.io/apps/omnicrm-ultimate"
echo "📝 Logs: flyctl logs"
echo "🔍 Status: flyctl status"
echo ""
echo "✨ OmniCRM Ultimate v7.0.0 is LIVE!"
echo "================================================"

unset FLY_API_TOKEN
