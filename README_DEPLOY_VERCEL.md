# دليل نشر الواجهة على Vercel (بالعربي)

مستوى: نشر الواجهة (Frontend) فقط على Vercel، والباكيند منفصل.

الخطوات الموصى بها:
1. افتح https://vercel.com/new وادمج المستودع admragy/NeuroCRM-GodMode.
2. في إعدادات المشروع (Project Settings) ضع Root Directory = frontend
3. أضف متغيّرات البيئة (Environment Variables) اللازمة:
   - NEXT_PUBLIC_SUPABASE_URL
   - NEXT_PUBLIC_SUPABASE_ANON_KEY
   - NEXT_PUBLIC_API_URL  ← رابط الباكيند (مثلاً https://your-backend.up.railway.app)
   - OPENAI_API_KEY (إذا تستخدمه في الواجهة)
4. تحقق أن package.json داخل frontend يحتوي على السكربت: `build` -> `next build`
5. اضغط Deploy.

نشر الباكيند (موصى به خارجيًا):
- أنشر FastAPI على Railway / Fly.io / Render (اقرأ ملفات `GITHUB_DEPLOYMENT_GUIDE.md` أو `fly.toml` في المشروع).
- اضبط متغيرات البيئة للباقيند: DATABASE_URL, REDIS_URL, SECRET_KEY, OPENAI_API_KEY, إلخ.
- بعد النشر انسخ رابط الباكيند وأضفه إلى NEXT_PUBLIC_API_URL في إعدادات Vercel.

ملاحظات فنية:
- WebSockets: إذا كان الباكيند يستخدم WebSockets فيجب التأكّد من أن المضيف يدعمها (Fly.io أو Railway يدعمان ذلك).
- قواعد البيانات: Vercel لا تستضيف PostgreSQL مباشرة، استخدم مزوّد خارجي.
