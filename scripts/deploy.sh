#!/bin/bash

# 🚀 OmniCRM Ultimate - Production Deployment Script
# =================================================
# Automated deployment with health checks and rollback

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
APP_NAME="omnicrm"
DEPLOY_DIR="/opt/omnicrm"
BACKUP_DIR="/opt/omnicrm/backups"
LOG_FILE="/var/log/omnicrm-deploy.log"

# Functions
log() {
    echo -e "${BLUE}[$(date +'%Y-%m-%d %H:%M:%S')]${NC} $1" | tee -a "$LOG_FILE"
}

success() {
    echo -e "${GREEN}✅ $1${NC}" | tee -a "$LOG_FILE"
}

error() {
    echo -e "${RED}❌ $1${NC}" | tee -a "$LOG_FILE"
}

warning() {
    echo -e "${YELLOW}⚠️  $1${NC}" | tee -a "$LOG_FILE"
}

# Pre-deployment checks
pre_deploy_checks() {
    log "🔍 Running pre-deployment checks..."
    
    # Check if running as root or with sudo
    if [ "$EUID" -ne 0 ]; then
        error "Please run with sudo or as root"
        exit 1
    fi
    
    # Check Docker
    if ! command -v docker &> /dev/null; then
        error "Docker is not installed"
        exit 1
    fi
    
    # Check Docker Compose
    if ! command -v docker-compose &> /dev/null; then
        error "Docker Compose is not installed"
        exit 1
    fi
    
    # Check .env file
    if [ ! -f ".env" ]; then
        error ".env file not found. Copy .env.production.template to .env and configure it."
        exit 1
    fi
    
    # Validate required environment variables
    source .env
    required_vars=("SECRET_KEY" "JWT_SECRET_KEY" "DATABASE_URL" "REDIS_URL")
    for var in "${required_vars[@]}"; do
        if [ -z "${!var}" ]; then
            error "Required environment variable $var is not set"
            exit 1
        fi
    done
    
    success "Pre-deployment checks passed"
}

# Create database backup
create_backup() {
    log "💾 Creating database backup..."
    
    timestamp=$(date +%Y%m%d_%H%M%S)
    backup_file="$BACKUP_DIR/pre_deploy_backup_$timestamp.sql"
    
    mkdir -p "$BACKUP_DIR"
    
    # Backup using Docker
    docker-compose exec -T postgres pg_dump -U omnicrm omnicrm_prod > "$backup_file" 2>/dev/null || {
        warning "Database backup failed (database might not exist yet)"
        return 0
    }
    
    if [ -f "$backup_file" ]; then
        success "Backup created: $backup_file"
    else
        error "Backup failed"
        exit 1
    fi
}

# Pull latest code
pull_code() {
    log "📥 Pulling latest code from GitHub..."
    
    git fetch origin
    git pull origin main
    
    success "Code updated"
}

# Build Docker images
build_images() {
    log "🏗️  Building Docker images..."
    
    docker-compose -f docker-compose.prod.yml build --no-cache
    
    success "Images built successfully"
}

# Run database migrations
run_migrations() {
    log "🗄️  Running database migrations..."
    
    docker-compose -f docker-compose.prod.yml run --rm app python -m alembic upgrade head
    
    success "Migrations completed"
}

# Start services
start_services() {
    log "🚀 Starting services..."
    
    docker-compose -f docker-compose.prod.yml up -d
    
    success "Services started"
}

# Health check
health_check() {
    log "🏥 Running health checks..."
    
    max_attempts=30
    attempt=0
    
    while [ $attempt -lt $max_attempts ]; do
        if curl -f http://localhost:8000/health > /dev/null 2>&1; then
            success "Health check passed"
            return 0
        fi
        
        attempt=$((attempt + 1))
        echo -n "."
        sleep 2
    done
    
    error "Health check failed after $max_attempts attempts"
    return 1
}

# Rollback
rollback() {
    error "Deployment failed! Rolling back..."
    
    # Stop new containers
    docker-compose -f docker-compose.prod.yml down
    
    # Restore from backup
    if [ -n "$backup_file" ] && [ -f "$backup_file" ]; then
        log "Restoring database from backup..."
        docker-compose -f docker-compose.prod.yml up -d postgres
        sleep 10
        docker-compose exec -T postgres psql -U omnicrm omnicrm_prod < "$backup_file"
    fi
    
    # Start old containers
    docker-compose -f docker-compose.prod.yml up -d
    
    error "Rollback completed"
    exit 1
}

# Main deployment flow
main() {
    log "🚀 Starting OmniCRM deployment..."
    
    # Pre-checks
    pre_deploy_checks
    
    # Backup
    create_backup
    
    # Pull code
    pull_code
    
    # Build
    build_images
    
    # Stop old containers
    log "🛑 Stopping old containers..."
    docker-compose -f docker-compose.prod.yml down
    
    # Start database first
    log "🗄️  Starting database..."
    docker-compose -f docker-compose.prod.yml up -d postgres redis
    sleep 10
    
    # Run migrations
    run_migrations
    
    # Start all services
    start_services
    
    # Health check
    if health_check; then
        success "🎉 Deployment completed successfully!"
        
        # Show status
        log "📊 Service status:"
        docker-compose -f docker-compose.prod.yml ps
        
        # Show logs
        log "📝 Recent logs:"
        docker-compose -f docker-compose.prod.yml logs --tail=50 app
        
    else
        rollback
    fi
}

# Run deployment
main
