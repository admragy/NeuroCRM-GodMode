# ⚡ Quick Start Guide - God Mode Business OS

## 🚀 5-Minute Setup

### Step 1: Clone & Install (2 min)
```bash
git clone https://github.com/admragy/OmniCRM-Ultimate.git
cd OmniCRM-Ultimate/frontend
npm install
```

### Step 2: Setup Supabase (2 min)
1. Go to [supabase.com](https://supabase.com) → Create project
2. Copy your project URL and anon key
3. In Supabase dashboard: SQL Editor → New Query
4. Paste content from `supabase-schema.sql` → Run

### Step 3: Configure Environment (1 min)
```bash
cp .env.example .env
nano .env  # Add your keys
```

Required:
```env
NEXT_PUBLIC_SUPABASE_URL=your_url_here
NEXT_PUBLIC_SUPABASE_ANON_KEY=your_key_here
OPENAI_API_KEY=your_openai_key_here
```

### Step 4: Launch God Mode
```bash
npm run dev
# Open: http://localhost:3000/dashboard
```

---

## 🎯 Test Each Module

### 1. Test Neuro-Sales Engine
Open browser console:
```javascript
import { analyzeCustomerPsychology } from '@/lib/openai/neuro-sales';

const result = await analyzeCustomerPsychology("السعر غالي، عندكم خصم؟");
console.log(result);
// Returns: { profile: "stingy", discount: 20%, confidence: 92% }
```

### 2. Test Competitor Radar
Add competitor via Supabase dashboard:
```sql
INSERT INTO competitors (name, url, current_price, product_name) 
VALUES ('Test Store', 'https://example.com/product', 499, 'Widget Pro');
```

Then in code:
```javascript
import { monitorCompetitor } from '@/lib/scrapers/competitor-radar';

await monitorCompetitor('comp-1', 'https://example.com/product', 'Test Store');
// Scrapes page and saves price
```

### 3. Test Auto-Pilot
Create test campaign:
```sql
INSERT INTO campaigns (name, platform, budget, total_spend, total_revenue) 
VALUES ('Test Ads', 'facebook', 1000, 500, 6000);
-- ROAS = 12x → Auto-Pilot will increase budget by 20%
```

Run Auto-Pilot:
```javascript
import { runAutoPilot } from '@/lib/automation/auto-pilot';

const actions = await runAutoPilot();
console.log(actions);
// Shows: Budget increased from $1000 to $1200 (ROAS 12x)
```

---

## 📊 Dashboard Overview

When you open `http://localhost:3000/dashboard`:

```
┌────────────────────────────────────────────┐
│  ⚡ GOD MODE BUSINESS OS                   │
│  Auto-Pilot: ● ACTIVE                     │
├────────────────────────────────────────────┤
│  💰 Revenue    📦 Orders    📊 Leads       │
│  Real-time     Real-time    Real-time     │
├────────────────────────────────────────────┤
│  🚨 LIVE ALERTS                            │
│  - Competitor price drop detected!         │
│  - Campaign #5 ROAS 12x - Budget scaled   │
└────────────────────────────────────────────┘
```

---

## 🔥 Pro Tips

1. **Enable Auto-Pilot First:**
   - Click "ACTIVATE" button in dashboard
   - It runs every 30 minutes automatically

2. **Add Your Competitors:**
   - Go to Supabase dashboard
   - Add competitor URLs to `competitors` table
   - System monitors them 24/7

3. **Test with Sample Data:**
   - Use the SQL comments in `supabase-schema.sql`
   - Uncomment the INSERT statements at the bottom

4. **Monitor Console:**
   - Check browser console for real-time logs
   - See AI decisions being made live

---

## 🐛 Troubleshooting

### "Missing Supabase variables"
```bash
# Make sure .env has:
NEXT_PUBLIC_SUPABASE_URL=https://xxx.supabase.co
NEXT_PUBLIC_SUPABASE_ANON_KEY=eyJxxx...
```

### "OpenAI API error"
```bash
# Check your API key is valid:
OPENAI_API_KEY=sk-xxx...

# Make sure you have credit:
# https://platform.openai.com/account/billing
```

### "RLS policy error"
```sql
-- Run this in Supabase SQL Editor:
ALTER TABLE orders ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Allow all for authenticated users"
ON orders FOR ALL
TO authenticated
USING (true);
```

---

## 📞 Need Help?

- 📧 Email: admragy@example.com
- 🐙 GitHub Issues: [Create Issue](https://github.com/admragy/OmniCRM-Ultimate/issues)
- 📖 Full Docs: See `README.md` in `/frontend` folder

---

**Ready to dominate? Let's go! ⚡**
