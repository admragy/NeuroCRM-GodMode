# 🐳 OmniCRM Ultimate - Production Docker Image
# Multi-stage build for minimal size and maximum security

# ========================================
# Stage 1: Build Frontend
# ========================================
FROM node:20-alpine AS frontend-builder

WORKDIR /app/frontend

# Copy package files
COPY frontend/package*.json ./

# Install dependencies
RUN npm ci --only=production

# Copy frontend source
COPY frontend/ ./

# Build Next.js application
RUN npm run build

# ========================================
# Stage 2: Build Backend Dependencies
# ========================================
FROM python:3.11-slim AS backend-builder

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir --user -r requirements.txt

# ========================================
# Stage 3: Final Production Image
# ========================================
FROM python:3.11-slim

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PORT=8000 \
    WORKERS=4

# Create non-root user
RUN groupadd -r omnicrm && useradd -r -g omnicrm omnicrm

WORKDIR /app

# Install runtime dependencies
RUN apt-get update && apt-get install -y \
    libpq5 \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy Python dependencies from builder
COPY --from=backend-builder /root/.local /home/omnicrm/.local

# Copy backend code
COPY --chown=omnicrm:omnicrm app/ ./app/
COPY --chown=omnicrm:omnicrm main.py .
COPY --chown=omnicrm:omnicrm migrations/ ./migrations/
COPY --chown=omnicrm:omnicrm scripts/ ./scripts/

# Copy frontend build
COPY --from=frontend-builder --chown=omnicrm:omnicrm /app/frontend/.next ./frontend/.next
COPY --from=frontend-builder --chown=omnicrm:omnicrm /app/frontend/public ./frontend/public
COPY --from=frontend-builder --chown=omnicrm:omnicrm /app/frontend/package*.json ./frontend/

# Create necessary directories
RUN mkdir -p logs backups uploads && \
    chown -R omnicrm:omnicrm logs backups uploads

# Switch to non-root user
USER omnicrm

# Add local Python packages to PATH
ENV PATH=/home/omnicrm/.local/bin:$PATH

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD curl -f http://localhost:${PORT}/health || exit 1

# Expose port
EXPOSE ${PORT}

# Start application
CMD ["sh", "-c", "uvicorn main:app --host 0.0.0.0 --port ${PORT} --workers ${WORKERS} --log-level info"]
