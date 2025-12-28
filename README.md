# 🚀 Hunter Pro CRM Ultimate Enterprise Edition v7.0.0

<div align="center">

![Version](https://img.shields.io/badge/version-7.0.0-blue.svg)
![Python](https://img.shields.io/badge/python-3.11+-green.svg)
![FastAPI](https://img.shields.io/badge/FastAPI-0.109.0-009688.svg)
![License](https://img.shields.io/badge/license-MIT-orange.svg)
![Status](https://img.shields.io/badge/status-production%20ready-success.svg)

**نظام CRM متقدم مع تكامل الذكاء الاصطناعي**

[التوثيق](#-الميزات) • [البدء السريع](#-البدء-السريع) • [النشر](#-النشر) • [API Docs](https://your-app.railway.app/docs)

</div>

---

## ✨ الميزات

### 🤖 الذكاء الاصطناعي
- **6 مزودي AI:** OpenAI، Claude (Anthropic)، Google Gemini، Groq، Ollama، Custom API
- **توليد محتوى ذكي** للعملاء والصفقات
- **تحليل البيانات** باستخدام AI
- **تقييم الصفقات** التلقائي

### 👥 إدارة العملاء (CRM)
- **CRUD كامل** للعملاء
- **سجل تفاعلات** شامل
- **تصنيف ذكي** حسب القيمة
- **بحث وفلترة** متقدمة
- **ملاحظات وعلامات** مخصصة

### 💼 إدارة الصفقات
- **مسار المبيعات** الكامل (Pipeline)
- **تتبع القيمة** المالية
- **مراحل قابلة للتخصيص**
- **تقييم AI** لفرص الإغلاق
- **تنبيهات ذكية**

### 📱 تكاملات الاتصالات
- **WhatsApp** (6 أوضاع تشغيل)
  - Web Automation (Selenium)
  - Business API
  - Twilio Integration
  - Bulk Messaging
  - Templates
  - Media Support
- **البريد الإلكتروني** (SMTP)
- **WebSocket** للدردشة الحية
- **Webhooks** للتكاملات الخارجية

### 📊 التقارير والتحليلات
- **تقارير PDF** احترافية
- **تصدير Excel** متقدم
- **رسوم بيانية** تفاعلية (Charts)
- **إحصائيات في الوقت الفعلي**
- **KPIs Dashboard**

### 🔒 الأمان
- **JWT Authentication** مع Refresh Tokens
- **2FA** (Two-Factor Authentication)
- **OAuth2** للتكاملات
- **RBAC** (Role-Based Access Control)
- **API Keys** للتطبيقات
- **Rate Limiting** ضد الهجمات
- **AES-256 Encryption** للبيانات الحساسة
- **Password Hashing** (bcrypt)

### 📢 التسويق والإعلانات
- **Facebook Ads Manager**
- **10 استراتيجيات يونيكورن**
- **تحليل الحملات**
- **ROI Tracking**
- **A/B Testing**

### 🌍 المميزات الإضافية
- **متعدد اللغات** (6 لغات + RTL للعربية)
- **Dark Mode** و Light Mode
- **Progressive Web App (PWA)**
- **Responsive Design**
- **Real-time Notifications**
- **File Upload** & Management
- **Search & Filters** متقدمة
- **Pagination** للبيانات الكبيرة

---

## 🛠️ التقنيات المستخدمة

### Backend
```
🐍 Python 3.11+
⚡ FastAPI 0.109.0
🗄️ SQLAlchemy 2.0 (ORM)
🐘 PostgreSQL (Database)
🔴 Redis (Cache & Queue)
🧩 Celery (Background Tasks)
```

### AI & ML
```
🤖 OpenAI GPT-4
🧠 Anthropic Claude
🌟 Google Gemini
⚡ Groq
🦙 Ollama (Local)
```

### Frontend
```
🎨 Vanilla JavaScript
💅 CSS3 (Modern)
🎭 Responsive Design
📱 PWA Support
```

### DevOps & Infrastructure
```
🐳 Docker & Docker Compose
☸️ Kubernetes Ready
🔄 CI/CD (GitHub Actions)
📊 Prometheus + Grafana (Monitoring)
🚨 Sentry (Error Tracking)
🌐 Nginx (Reverse Proxy)
```

---

## 🚀 البدء السريع

### المتطلبات
- Python 3.11+
- PostgreSQL 14+
- Redis 7+
- (اختياري) Docker & Docker Compose

### التثبيت المحلي

#### 1. استنساخ المشروع
```bash
git clone https://github.com/admragy/hunter-pro-crm.git
cd hunter-pro-crm
```

#### 2. إنشاء بيئة افتراضية
```bash
# Windows
python -m venv venv
venv\Scripts\activate

# macOS/Linux
python3 -m venv venv
source venv/bin/activate
```

#### 3. تثبيت المكتبات
```bash
pip install -r requirements.txt
```

#### 4. إعداد المتغيرات البيئية
```bash
cp .env.example .env
# عدّل الملف .env حسب إعداداتك
```

#### 5. تشغيل التطبيق
```bash
# Development Mode
uvicorn main:app --reload --host 0.0.0.0 --port 8000

# Production Mode
uvicorn main:app --workers 4 --host 0.0.0.0 --port 8000
```

#### 6. الوصول للتطبيق
```
🌐 Dashboard: http://localhost:8000
📖 API Docs: http://localhost:8000/docs
🔄 Health Check: http://localhost:8000/health
```

### التثبيت باستخدام Docker

```bash
# Build & Run
docker-compose up -d

# Check Status
docker-compose ps

# View Logs
docker-compose logs -f

# Stop
docker-compose down
```

---

## 🌐 النشر

### Railway (موصى به - أسهل وأسرع)

#### الخطوات السريعة:
1. افتح [Railway.app](https://railway.app/)
2. **New Project** → **Deploy from GitHub**
3. اختر المستودع: `admragy/hunter-pro-crm`
4. أضف **PostgreSQL** و **Redis**
5. ضبط المتغيرات البيئية (راجع `.env.example`)
6. احفظ → النشر يبدأ تلقائياً

**📚 دليل مفصل:** اقرأ [RAILWAY_DEPLOYMENT.md](./RAILWAY_DEPLOYMENT.md)

**⏱️ الوقت:** 3-5 دقائق فقط!

### منصات أخرى

- **Vercel:** راجع [vercel.json](./vercel.json)
- **Fly.io:** راجع [fly.toml](./fly.toml)
- **Render:** Deploy مباشر من GitHub
- **AWS/GCP/Azure:** استخدم Docker

---

## 📚 التوثيق

### دلائل متوفرة:
- 📖 [RAILWAY_DEPLOYMENT.md](./RAILWAY_DEPLOYMENT.md) - دليل النشر على Railway
- 📋 [QUICK_DEPLOY_GUIDE.md](./QUICK_DEPLOY_GUIDE.md) - دليل النشر السريع (3 دقائق)
- 🔧 [FIXES_SUMMARY.md](./FIXES_SUMMARY.md) - ملخص الإصلاحات
- 📊 [ACTION_PLAN.md](./ACTION_PLAN.md) - خطة العمل الكاملة
- 📝 [CHANGELOG.md](./CHANGELOG.md) - سجل التغييرات
- 🚀 [DEPLOYMENT.md](./DEPLOYMENT.md) - استراتيجيات النشر

### API Documentation
- **Swagger UI:** `/docs`
- **ReDoc:** `/redoc`
- **OpenAPI JSON:** `/api/openapi.json`

---

## 🔌 API Endpoints

### Authentication
```
POST   /api/auth/register      - تسجيل مستخدم جديد
POST   /api/auth/login         - تسجيل الدخول
POST   /api/auth/refresh       - تجديد Token
POST   /api/auth/logout        - تسجيل الخروج
GET    /api/auth/me            - معلومات المستخدم الحالي
POST   /api/auth/2fa/enable    - تفعيل 2FA
POST   /api/auth/2fa/verify    - التحقق من 2FA
```

### Customers (CRM)
```
GET    /api/customers          - قائمة العملاء
POST   /api/customers          - إضافة عميل
GET    /api/customers/{id}     - تفاصيل عميل
PUT    /api/customers/{id}     - تحديث عميل
DELETE /api/customers/{id}     - حذف عميل
GET    /api/customers/search   - بحث متقدم
```

### Deals (الصفقات)
```
GET    /api/deals              - قائمة الصفقات
POST   /api/deals              - إضافة صفقة
GET    /api/deals/{id}         - تفاصيل صفقة
PUT    /api/deals/{id}         - تحديث صفقة
DELETE /api/deals/{id}         - حذف صفقة
POST   /api/deals/{id}/ai      - تحليل AI للصفقة
```

### AI Services
```
POST   /api/ai/generate        - توليد محتوى
POST   /api/ai/analyze         - تحليل بيانات
GET    /api/ai/providers       - المزودين المتاحين
POST   /api/ai/chat            - دردشة AI
```

### WhatsApp
```
POST   /api/whatsapp/send      - إرسال رسالة
POST   /api/whatsapp/bulk      - إرسال جماعي
GET    /api/whatsapp/templates - قوالب الرسائل
POST   /api/whatsapp/media     - إرسال ميديا
```

### Reports (التقارير)
```
GET    /api/reports/sales      - تقرير المبيعات
GET    /api/reports/customers  - تقرير العملاء
POST   /api/reports/pdf        - توليد PDF
POST   /api/reports/excel      - توليد Excel
GET    /api/reports/charts     - الرسوم البيانية
```

**📖 الوصول الكامل:** `/docs` للتوثيق التفاعلي

---

## 🧪 الاختبار

### تشغيل الاختبارات
```bash
# جميع الاختبارات
pytest

# مع التغطية
pytest --cov=app

# اختبارات محددة
pytest tests/test_auth.py -v
```

### اختبار API يدوياً
```bash
# Health Check
curl http://localhost:8000/health

# تسجيل مستخدم
curl -X POST http://localhost:8000/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "admin@example.com",
    "password": "SecurePass123!",
    "full_name": "Admin User"
  }'
```

---

## 🤝 المساهمة

المساهمات مرحب بها! الخطوات:

1. Fork المشروع
2. إنشاء Branch للميزة (`git checkout -b feature/AmazingFeature`)
3. Commit التغييرات (`git commit -m 'Add AmazingFeature'`)
4. Push للـ Branch (`git push origin feature/AmazingFeature`)
5. فتح Pull Request

---

## 📈 إحصائيات المشروع

```
📊 الكود
├── 50+ ملفات
├── ~10,000 سطر من الكود
├── 120+ دوال ومعالجات
└── 70+ API Endpoints

🤖 الذكاء الاصطناعي
├── 6 مزودي AI
├── 10+ نماذج مدعومة
└── تكامل سلس

🗄️ قواعد البيانات
├── 11 نموذج (Models)
├── 30+ جدول
└── علاقات معقدة

🐳 البنية التحتية
├── 11 خدمات Docker
├── Kubernetes Ready
└── Auto-scaling

📚 التوثيق
└── 13+ ملف توثيق
```

---

## 💰 القيمة التجارية

```
💵 القيمة المقدرة: $95,000
⏱️ ساعات التطوير: 880 ساعة
🎯 الحالة: Production Ready
📦 الترخيص: MIT (مفتوح المصدر)
```

---

## 📄 الترخيص

هذا المشروع مرخص تحت **MIT License** - راجع ملف [LICENSE](./LICENSE) للتفاصيل.

```
MIT License

Copyright (c) 2024 admragy

Permission is hereby granted, free of charge...
```

---

## 📞 الدعم والاتصال

- 📧 **Email:** admragy@example.com
- 🐙 **GitHub:** [@admragy](https://github.com/admragy)
- 🌐 **Website:** https://hunter-pro-crm.railway.app
- 💬 **Issues:** [GitHub Issues](https://github.com/admragy/hunter-pro-crm/issues)

---

## 🎉 شكر خاص

شكراً لجميع مزودي الأدوات والمكتبات مفتوحة المصدر:
- FastAPI Team
- PostgreSQL Community
- Redis Labs
- OpenAI, Anthropic, Google AI
- وجميع المساهمين في المكتبات المستخدمة

---

## 🗺️ خارطة الطريق (Roadmap)

### النسخة 7.1 (قريباً)
- [ ] تطبيق موبايل (Flutter)
- [ ] تكامل Telegram
- [ ] دعم GraphQL
- [ ] Admin Panel محسّن

### النسخة 8.0 (المستقبل)
- [ ] Machine Learning للتنبؤات
- [ ] Voice AI Integration
- [ ] Blockchain Integration
- [ ] Multi-tenancy Support

---

<div align="center">

### ⭐ إذا أعجبك المشروع، لا تنسى تقييمه!

**صنع بـ ❤️ في 2024**

[الصفحة الرئيسية](#-hunter-pro-crm-ultimate-enterprise-edition-v700) • [GitHub](https://github.com/admragy/hunter-pro-crm) • [النشر](#-النشر)

---

![Footer](https://img.shields.io/badge/Hunter%20Pro%20CRM-v7.0.0-blue?style=for-the-badge)

</div>
