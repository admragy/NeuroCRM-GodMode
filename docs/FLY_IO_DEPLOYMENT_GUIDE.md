# 🚀 **دليل النشر على Fly.io**

## 📋 **المتطلبات**

1. **حساب Fly.io**: قم بالتسجيل على [fly.io](https://fly.io)
2. **flyctl CLI**: ثبّت أداة flyctl
   ```bash
   # Mac/Linux
   curl -L https://fly.io/install.sh | sh
   
   # Windows (PowerShell)
   pwsh -Command "iwr https://fly.io/install.ps1 -useb | iex"
   ```
3. **Docker**: تأكد من تثبيت Docker (للبناء المحلي)

---

## ⚡ **خطوات النشر السريعة**

### **1. تسجيل الدخول**
```bash
flyctl auth login
```

### **2. إعداد المتغيرات البيئية**
```bash
# انسخ ملف .env.example إلى .env
cp .env.example .env

# عدّل الملف وأضف مفاتيحك الحقيقية
nano .env
```

### **3. إنشاء التطبيق (أول مرة فقط)**
```bash
flyctl apps create neurocrm-godmode-v1
```

### **4. رفع الأسرار (Environment Variables)**
```bash
# رفع جميع المتغيرات من .env
cat .env | flyctl secrets import

# أو رفع متغير واحد
flyctl secrets set DATABASE_URL="postgresql://..."
```

### **5. النشر!**
```bash
# خيار 1: باستخدام السكريبت الآلي (موصى به)
./deploy_fly.sh

# خيار 2: يدوياً
flyctl deploy --remote-only
```

---

## 🔧 **التكوين المتقدم**

### **تغيير اسم التطبيق**
```toml
# fly.toml
app = "your-unique-app-name"  # غيّر هذا
```

### **تغيير المنطقة (Region)**
```bash
# عرض المناطق المتاحة
flyctl platform regions

# تغيير المنطقة
flyctl regions set ams  # Amsterdam
flyctl regions set fra  # Frankfurt
flyctl regions set dub  # Dubai (قريب من السعودية)
```

### **تعديل الموارد**
```bash
# عرض الموارد الحالية
flyctl scale show

# زيادة الذاكرة
flyctl scale memory 512  # MB

# زيادة عدد الـ VMs
flyctl scale count 2
```

---

## 🗄️ **إعداد قاعدة البيانات**

### **خيار 1: Fly Postgres (موصى به)**
```bash
# إنشاء قاعدة بيانات
flyctl postgres create --name neurocrm-db

# ربطها بالتطبيق
flyctl postgres attach neurocrm-db

# سيتم تعيين DATABASE_URL تلقائياً!
```

### **خيار 2: Supabase (مجاني + Real-time)**
```bash
# احصل على DATABASE_URL من Supabase Dashboard
# أضفه للأسرار:
flyctl secrets set DATABASE_URL="postgresql://postgres:xxx@xxx.supabase.co:5432/postgres"
```

### **خيار 3: Neon (Serverless Postgres)**
```bash
# احصل على DATABASE_URL من Neon Dashboard
flyctl secrets set DATABASE_URL="postgresql://xxx@xxx.neon.tech/xxx"
```

---

## 📊 **المراقبة والصيانة**

### **عرض السجلات (Logs)**
```bash
# سجلات حية
flyctl logs

# آخر 100 سطر
flyctl logs --max 100
```

### **فحص الصحة (Health Check)**
```bash
# حالة التطبيق
flyctl status

# معلومات تفصيلية
flyctl info
```

### **SSH إلى الخادم**
```bash
# الدخول للخادم
flyctl ssh console

# تشغيل أمر مباشر
flyctl ssh console -C "python manage.py migrate"
```

### **إعادة التشغيل**
```bash
flyctl apps restart neurocrm-godmode-v1
```

---

## 🔐 **الأمان وأفضل الممارسات**

### **1. استخدم Secrets لكل المتغيرات الحساسة**
```bash
# ❌ خطأ: وضع المفاتيح في fly.toml
# ✅ صحيح: استخدام secrets
flyctl secrets set OPENAI_API_KEY="sk-..."
```

### **2. فعّل HTTPS (مفعّل افتراضياً)**
```toml
# fly.toml
[[services.ports]]
  port = 80
  handlers = ["http"]
  force_https = true  # ✅
```

### **3. قيّد الوصول بـ CORS**
```bash
flyctl secrets set CORS_ORIGINS="https://yourdomain.com"
```

### **4. استخدم Sentry للمراقبة**
```bash
flyctl secrets set SENTRY_DSN="https://xxx@sentry.io/xxx"
```

---

## 💰 **التكلفة والاستخدام**

### **الباقة المجانية (Hobby Plan)**
```yaml
ما تحصل عليه مجاناً:
  - 3 VMs مشتركة (shared)
  - 256 MB RAM لكل VM
  - 3 GB تخزين
  - 160 GB نقل بيانات/شهر
  
تكفي لـ:
  - 1,000-5,000 زيارة/يوم
  - مشاريع صغيرة ومتوسطة
  - اختبار وتطوير
```

### **الباقة المدفوعة (Launch Plan)**
```yaml
$5-20/شهر:
  - 1 GB RAM
  - 10 GB تخزين
  - Unlimited نقل بيانات
  
تكفي لـ:
  - 10,000-50,000 زيارة/يوم
  - تطبيقات إنتاجية
  - أداء أفضل
```

---

## 🚨 **حل المشاكل الشائعة**

### **1. Build Failed**
```bash
# تحقق من Dockerfile
cat Dockerfile

# تحقق من requirements.txt
cat requirements.txt

# جرب بناء محلي
docker build -t neurocrm .
```

### **2. App Crashed**
```bash
# عرض السجلات
flyctl logs

# تحقق من الصحة
flyctl status

# إعادة تشغيل
flyctl apps restart
```

### **3. Database Connection Failed**
```bash
# تحقق من DATABASE_URL
flyctl secrets list

# اختبر الاتصال
flyctl ssh console
python -c "import psycopg2; psycopg2.connect('$DATABASE_URL')"
```

### **4. Secrets Not Loading**
```bash
# تأكد من رفعها
flyctl secrets list

# أعد رفعها
cat .env | flyctl secrets import
```

---

## 📈 **التحديثات والنشر المستمر**

### **نشر تحديث**
```bash
# 1. اعمل commit للتغييرات
git add .
git commit -m "Update: feature X"

# 2. انشر على Fly.io
./deploy_fly.sh

# أو
flyctl deploy --remote-only
```

### **Rollback (العودة لنسخة سابقة)**
```bash
# عرض النسخ السابقة
flyctl releases

# العودة لنسخة معينة
flyctl releases rollback <version>
```

---

## 🌍 **نشر متعدد المناطق (Multi-Region)**

### **إضافة منطقة جديدة**
```bash
# إضافة منطقة
flyctl regions add dub  # Dubai
flyctl regions add jed  # Jeddah (إذا متاحة)

# عرض المناطق النشطة
flyctl regions list
```

### **توزيع التطبيق**
```bash
# زيادة عدد الـ VMs
flyctl scale count 3

# Fly.io سيوزعهم تلقائياً على المناطق
```

---

## 📞 **الدعم والمساعدة**

```yaml
Fly.io Community:
  - Forum: https://community.fly.io
  - Discord: https://fly.io/discord
  - Docs: https://fly.io/docs

OmniCRM God Mode:
  - GitHub: https://github.com/admragy/NeuroCRM-GodMode
  - Issues: https://github.com/admragy/NeuroCRM-GodMode/issues
  - Documentation: /docs
```

---

## ✅ **Checklist قبل الإطلاق**

```yaml
[ ] flyctl مثبت ومسجل دخول
[ ] .env معبأ بالمفاتيح الحقيقية
[ ] DATABASE_URL صحيح ويعمل
[ ] Secrets تم رفعها (flyctl secrets list)
[ ] Dockerfile يبني بنجاح محلياً
[ ] fly.toml مكون بشكل صحيح
[ ] اسم التطبيق فريد (app name)
[ ] المنطقة مناسبة (region)
[ ] الموارد كافية (RAM/CPU)
[ ] CORS مكون بشكل صحيح
[ ] Monitoring مفعل (Sentry)
[ ] Backup strategy جاهزة
```

---

**تم! الآن يمكنك نشر OmniCRM God Mode على Fly.io في دقائق! 🚀**

**Last Updated**: January 5, 2026  
**Version**: 1.0  
**Made with ❤️ in Saudi Arabia** 🇸🇦
