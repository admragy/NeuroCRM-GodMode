# 🚂 Railway Deployment Guide - OmniCRM Ultimate Enterprise v7.0.0

## 📋 Overview
Complete deployment guide for OmniCRM Ultimate Enterprise on Railway with all services and integrations.

---

## 🎯 Prerequisites

### Required
- ✅ Railway account (https://railway.app)
- ✅ Railway CLI installed
- ✅ GitHub account with OmniCRM-Ultimate repository
- ✅ Railway API Token

### External Services
- Facebook Developer Account (for Facebook Ads)
- WhatsApp Business API access
- OpenAI API key (or other AI provider)
- Email service (SendGrid/Mailgun)

---

## 🚀 Quick Deployment (8-10 minutes)

### Step 1: Login to Railway CLI
```bash
# Install Railway CLI
npm install -g @railway/cli

# Login with your token
export RAILWAY_TOKEN="YOUR_RAILWAY_TOKEN"
railway login
```

### Step 2: Link to Existing Project
```bash
cd /path/to/OmniCRM-Ultimate
railway link 4c700acd-f97a-453f-bdc3-6672fa264ef2
```

### Step 3: Add Required Services

#### 3.1 PostgreSQL Database
```bash
railway add postgresql
```
**Note**: Railway will automatically set `DATABASE_URL` environment variable

#### 3.2 Redis Cache
```bash
railway add redis
```
**Note**: Railway will automatically set `REDIS_URL` environment variable

#### 3.3 Qdrant Vector Database (Optional)
```bash
railway add qdrant
```
Or use external Qdrant Cloud (https://cloud.qdrant.io)

---

## ⚙️ Environment Variables Configuration

### Core Application Settings
```bash
# Application
ENVIRONMENT=production
DEBUG=False
APP_NAME=OmniCRM Ultimate Enterprise
APP_VERSION=7.0.0
HOST=0.0.0.0
PORT=5000

# Security (GENERATE NEW KEYS!)
SECRET_KEY=your-super-secret-key-here-change-this
JWT_SECRET_KEY=your-jwt-secret-key-here-change-this
JWT_ALGORITHM=HS256
JWT_EXPIRATION_MINUTES=10080
ENCRYPTION_KEY=your-encryption-key-32-chars
AES_KEY=your-aes-key-32-characters

# CORS
CORS_ORIGINS=["https://your-domain.com"]
```

### Database & Cache (Auto-configured by Railway)
```bash
# PostgreSQL - Auto-set by Railway
DATABASE_URL=${{Postgres.DATABASE_URL}}

# Redis - Auto-set by Railway  
REDIS_URL=${{Redis.REDIS_URL}}
```

### AI Providers Configuration
```bash
# Default AI Provider
DEFAULT_AI_PROVIDER=openai

# OpenAI (GPT-4)
OPENAI_API_KEY=sk-your-openai-api-key
OPENAI_MODEL=gpt-4-turbo-preview

# Anthropic Claude
ANTHROPIC_API_KEY=sk-ant-your-anthropic-key
ANTHROPIC_MODEL=claude-3-5-sonnet-20240620

# Google Gemini
GOOGLE_API_KEY=your-google-api-key
GEMINI_FLASH_MODEL=gemini-1.5-flash
GEMINI_PRO_MODEL=gemini-1.5-pro

# Groq (Fast Inference)
GROQ_API_KEY=gsk_your-groq-api-key
GROQ_MODEL=llama-3.1-70b-versatile

# Ollama (Self-hosted - Optional)
OLLAMA_BASE_URL=http://ollama:11434
OLLAMA_MODEL=llama3:8b
```

### Facebook Ads Integration 🎯
```bash
# Facebook Business
FACEBOOK_APP_ID=your-facebook-app-id
FACEBOOK_APP_SECRET=your-facebook-app-secret
FACEBOOK_ACCESS_TOKEN=your-long-lived-access-token
FACEBOOK_BUSINESS_ACCOUNT_ID=act_your-business-account-id
FACEBOOK_PIXEL_ID=your-pixel-id

# Webhook
FACEBOOK_WEBHOOK_VERIFY_TOKEN=your-webhook-verify-token
```

### WhatsApp Business API Integration 📱
```bash
# WhatsApp Business
WHATSAPP_PHONE_NUMBER_ID=your-phone-number-id
WHATSAPP_BUSINESS_ACCOUNT_ID=your-business-account-id
WHATSAPP_ACCESS_TOKEN=your-whatsapp-access-token
WHATSAPP_WEBHOOK_VERIFY_TOKEN=your-webhook-verify-token
WHATSAPP_API_VERSION=v18.0
```

### Email Service
```bash
# SendGrid
SENDGRID_API_KEY=SG.your-sendgrid-api-key
SMTP_FROM_EMAIL=noreply@yourdomain.com
SMTP_FROM_NAME=OmniCRM Ultimate

# OR Mailgun
MAILGUN_API_KEY=your-mailgun-api-key
MAILGUN_DOMAIN=mg.yourdomain.com
```

### Vector Database (Qdrant)
```bash
# Qdrant Cloud
QDRANT_URL=https://your-cluster.qdrant.io
QDRANT_API_KEY=your-qdrant-api-key
QDRANT_COLLECTION_NAME=omnicrm_embeddings

# OR Railway Qdrant
QDRANT_URL=${{Qdrant.QDRANT_URL}}
```

---

## 🔧 Railway CLI Deployment

### Method 1: Using Railway CLI (Recommended)
```bash
# Navigate to project directory
cd /path/to/OmniCRM-Ultimate

# Link to Railway project
railway link 4c700acd-f97a-453f-bdc3-6672fa264ef2

# Set environment variables
railway variables set ENVIRONMENT=production
railway variables set DEBUG=False
railway variables set SECRET_KEY="your-secret-key"
railway variables set JWT_SECRET_KEY="your-jwt-key"

# Deploy
railway up
```

### Method 2: GitHub Integration (Automatic)
1. Go to Railway Dashboard: https://railway.app/dashboard
2. Open project: OmniCRM-Ultimate
3. Click "Settings" → "Connect GitHub Repository"
4. Select: admragy/OmniCRM-Ultimate
5. Set branch: main
6. Enable "Auto-deploy on push"

---

## 📦 Services Architecture

```
┌─────────────────────────────────────────┐
│         Railway Project                 │
│     OmniCRM-Ultimate Enterprise         │
└─────────────────────────────────────────┘
                 │
    ┌────────────┼────────────┐
    │            │            │
    ▼            ▼            ▼
┌─────────┐  ┌─────────┐  ┌─────────┐
│FastAPI  │  │Postgres │  │ Redis   │
│App      │  │Database │  │ Cache   │
└─────────┘  └─────────┘  └─────────┘
    │            │            │
    └────────────┼────────────┘
                 │
    ┌────────────┼────────────┐
    │            │            │
    ▼            ▼            ▼
┌─────────┐  ┌─────────┐  ┌─────────┐
│Facebook │  │WhatsApp │  │AI APIs  │
│Ads API  │  │Business │  │6 Models │
└─────────┘  └─────────┘  └─────────┘
```

---

## 🔐 Security Configuration

### Generate Secure Keys
```python
# Run this to generate secure keys
import secrets
import string

def generate_key(length=32):
    alphabet = string.ascii_letters + string.digits
    return ''.join(secrets.choice(alphabet) for _ in range(length))

print(f"SECRET_KEY={generate_key(64)}")
print(f"JWT_SECRET_KEY={generate_key(64)}")
print(f"ENCRYPTION_KEY={generate_key(32)}")
print(f"AES_KEY={generate_key(32)}")
```

### Railway Secrets Management
```bash
# Set secrets via CLI
railway variables set SECRET_KEY="$(openssl rand -base64 64)"
railway variables set JWT_SECRET_KEY="$(openssl rand -base64 64)"
railway variables set ENCRYPTION_KEY="$(openssl rand -base64 32)"
```

---

## 🧪 Health Checks

### 1. Application Health
```bash
curl https://omnicrm-ultimate-production.up.railway.app/health
```

Expected Response:
```json
{
  "status": "healthy",
  "version": "7.0.0",
  "environment": "production",
  "services": {
    "database": "connected",
    "redis": "connected",
    "ai_service": "operational"
  }
}
```

### 2. API Documentation
```bash
# Swagger UI
https://omnicrm-ultimate-production.up.railway.app/docs

# ReDoc
https://omnicrm-ultimate-production.up.railway.app/redoc
```

### 3. Database Connection Test
```bash
curl https://omnicrm-ultimate-production.up.railway.app/api/v1/health/db
```

---

## 📊 Monitoring & Logs

### View Logs
```bash
# Real-time logs
railway logs

# Follow logs
railway logs --follow

# Specific service logs
railway logs --service web
```

### Resource Monitoring
```bash
# Check resource usage
railway status

# View metrics in Dashboard
# https://railway.app/project/4c700acd-f97a-453f-bdc3-6672fa264ef2/metrics
```

---

## 🔗 Webhook Configuration

### Facebook Ads Webhook
1. Go to Facebook App Dashboard
2. Navigate to Webhooks
3. Add Callback URL:
   ```
   https://omnicrm-ultimate-production.up.railway.app/api/v1/webhooks/facebook
   ```
4. Set Verify Token: `FACEBOOK_WEBHOOK_VERIFY_TOKEN`
5. Subscribe to:
   - `ads_insights`
   - `ads_management`
   - `lead_generation`

### WhatsApp Webhook
1. Go to WhatsApp Business Platform
2. Configure Webhook:
   ```
   https://omnicrm-ultimate-production.up.railway.app/api/v1/webhooks/whatsapp
   ```
3. Set Verify Token: `WHATSAPP_WEBHOOK_VERIFY_TOKEN`
4. Subscribe to:
   - `messages`
   - `message_status`
   - `contacts`

---

## 🚀 Post-Deployment Checklist

### ✅ Immediate Tasks
- [ ] Verify all services are running
- [ ] Test health endpoint
- [ ] Check API documentation loads
- [ ] Verify database connection
- [ ] Test Redis cache
- [ ] Confirm AI provider connectivity

### ✅ Integration Testing
- [ ] Test Facebook Ads API connection
- [ ] Verify WhatsApp Business API
- [ ] Send test email
- [ ] Create test campaign
- [ ] Send test WhatsApp message
- [ ] Check webhook delivery

### ✅ Security
- [ ] Rotate all default keys
- [ ] Enable Railway 2FA
- [ ] Configure custom domain with SSL
- [ ] Set up rate limiting
- [ ] Enable CORS properly
- [ ] Review environment variables

### ✅ Monitoring
- [ ] Set up uptime monitoring
- [ ] Configure error alerts
- [ ] Enable log aggregation
- [ ] Set up performance monitoring
- [ ] Configure backup schedules

---

## 📈 Scaling Configuration

### Horizontal Scaling
```toml
# railway.toml
[deploy]
replicas = 3
```

### Resource Allocation
```bash
# Set via Railway Dashboard
Memory: 2GB
CPU: 2 vCPU
```

---

## 🔄 Continuous Deployment

### Automatic Deployment
- Push to `main` branch → Auto-deploy on Railway
- Pull Request → Preview deployment
- Tags → Production releases

### Deployment Commands
```bash
# Deploy specific branch
railway up --branch staging

# Deploy with specific service
railway up --service web

# Rollback to previous version
railway rollback
```

---

## 💰 Estimated Costs

### Railway Services (Monthly)
- **Hobby Plan**: $5/month
  - 512 MB RAM
  - Shared CPU
  - 100 GB bandwidth

- **Developer Plan**: $20/month
  - 8 GB RAM
  - 8 vCPU
  - 100 GB bandwidth

- **Team Plan**: $99/month
  - 32 GB RAM
  - 32 vCPU
  - 500 GB bandwidth

### Additional Services
- PostgreSQL: Included
- Redis: Included
- Qdrant: $0-25/month (depending on usage)
- AI APIs: Variable based on usage
- Facebook/WhatsApp: Free API access

---

## 🆘 Troubleshooting

### Common Issues

#### 1. Database Connection Failed
```bash
# Check DATABASE_URL variable
railway variables get DATABASE_URL

# Restart service
railway restart
```

#### 2. Redis Connection Timeout
```bash
# Verify Redis service is running
railway status

# Check Redis URL
railway variables get REDIS_URL
```

#### 3. Build Failures
```bash
# Check build logs
railway logs --build

# Clear build cache
railway build --clear-cache
```

#### 4. Environment Variable Issues
```bash
# List all variables
railway variables

# Verify specific variable
railway variables get SECRET_KEY
```

---

## 📚 Additional Resources

### Documentation
- Railway Docs: https://docs.railway.app
- FastAPI Docs: https://fastapi.tiangolo.com
- PostgreSQL Docs: https://www.postgresql.org/docs
- Redis Docs: https://redis.io/documentation

### Support
- Railway Discord: https://discord.gg/railway
- GitHub Issues: https://github.com/admragy/OmniCRM-Ultimate/issues
- Email: support@omnicrm.com

---

## 🎉 Success Indicators

✅ **Deployment Successful When:**
1. Health endpoint returns 200 OK
2. API documentation loads correctly
3. Database migrations completed
4. All AI providers connected
5. Facebook Ads API working
6. WhatsApp Business API operational
7. Webhooks receiving events
8. Email service sending
9. Real-time features active
10. Logs showing no errors

---

## 🔮 Next Steps

### Phase 1: Initial Testing (Week 1)
- Run integration tests
- Verify all APIs
- Test webhook delivery
- Monitor performance

### Phase 2: Production Optimization (Week 2-4)
- Fine-tune AI responses
- Optimize database queries
- Configure caching strategies
- Set up CDN for static assets

### Phase 3: Advanced Features (Month 2+)
- Implement A/B testing
- Add advanced analytics
- Deploy AI model fine-tuning
- Integrate additional channels

---

**🚀 OmniCRM Ultimate Enterprise v7.0.0**
**Production Ready | Deployed on Railway**
**Value: $120,000+ | Status: Active**

---

*Last Updated: 30 December 2024*
*Deployment ID: 4c700acd-f97a-453f-bdc3-6672fa264ef2*
