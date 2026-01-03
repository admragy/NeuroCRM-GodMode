-- ============================================
-- OmniCRM Ultimate - God Mode Business OS
-- Supabase Database Schema
-- ============================================

-- Enable UUID extension
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- ============================================
-- ORDERS TABLE
-- ============================================
CREATE TABLE IF NOT EXISTS orders (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  customer_id UUID REFERENCES auth.users(id),
  total_amount DECIMAL(10, 2) NOT NULL,
  status VARCHAR(20) CHECK (status IN ('pending', 'completed', 'cancelled')) DEFAULT 'pending',
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Row Level Security
ALTER TABLE orders ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Users can view their own orders"
  ON orders FOR SELECT
  USING (auth.uid() = customer_id);

CREATE POLICY "System can insert orders"
  ON orders FOR INSERT
  WITH CHECK (true);

-- ============================================
-- LEADS TABLE
-- ============================================
CREATE TABLE IF NOT EXISTS leads (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  name VARCHAR(255) NOT NULL,
  phone VARCHAR(50),
  email VARCHAR(255),
  status VARCHAR(20) CHECK (status IN ('new', 'contacted', 'converted', 'lost')) DEFAULT 'new',
  source VARCHAR(100),
  psycho_profile VARCHAR(50), -- stingy, hesitant, vip, urgent, etc.
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Row Level Security
ALTER TABLE leads ENABLE ROW LEVEL SECURITY;

CREATE POLICY "All authenticated users can view leads"
  ON leads FOR SELECT
  TO authenticated
  USING (true);

-- ============================================
-- CAMPAIGNS TABLE
-- ============================================
CREATE TABLE IF NOT EXISTS campaigns (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  name VARCHAR(255) NOT NULL,
  platform VARCHAR(20) CHECK (platform IN ('facebook', 'google', 'tiktok')) NOT NULL,
  budget DECIMAL(10, 2) NOT NULL,
  total_spend DECIMAL(10, 2) DEFAULT 0,
  total_revenue DECIMAL(10, 2) DEFAULT 0,
  status VARCHAR(20) CHECK (status IN ('active', 'paused', 'stopped')) DEFAULT 'active',
  last_optimized TIMESTAMP WITH TIME ZONE,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

ALTER TABLE campaigns ENABLE ROW LEVEL SECURITY;

CREATE POLICY "All authenticated users can view campaigns"
  ON campaigns FOR SELECT
  TO authenticated
  USING (true);

-- ============================================
-- COMPETITORS TABLE
-- ============================================
CREATE TABLE IF NOT EXISTS competitors (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  name VARCHAR(255) NOT NULL,
  url TEXT NOT NULL,
  current_price DECIMAL(10, 2) NOT NULL,
  previous_price DECIMAL(10, 2) DEFAULT 0,
  price_change_percentage DECIMAL(5, 2) DEFAULT 0,
  product_name VARCHAR(255) NOT NULL,
  stock_status VARCHAR(20) CHECK (stock_status IN ('in_stock', 'out_of_stock', 'low_stock')) DEFAULT 'in_stock',
  promo_text TEXT,
  last_checked TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

ALTER TABLE competitors ENABLE ROW LEVEL SECURITY;

CREATE POLICY "All authenticated users can view competitors"
  ON competitors FOR SELECT
  TO authenticated
  USING (true);

-- ============================================
-- COMPETITOR ALERTS TABLE
-- ============================================
CREATE TABLE IF NOT EXISTS competitor_alerts (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  competitor_id UUID REFERENCES competitors(id) ON DELETE CASCADE,
  alert_type VARCHAR(50) NOT NULL,
  message TEXT NOT NULL,
  urgency VARCHAR(20) CHECK (urgency IN ('low', 'medium', 'high', 'critical')) NOT NULL,
  suggested_action JSONB,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

ALTER TABLE competitor_alerts ENABLE ROW LEVEL SECURITY;

CREATE POLICY "All authenticated users can view competitor alerts"
  ON competitor_alerts FOR SELECT
  TO authenticated
  USING (true);

-- ============================================
-- CONVERSATIONS HISTORY TABLE (Data Vacuum)
-- ============================================
CREATE TABLE IF NOT EXISTS conversations_history (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  source VARCHAR(20) CHECK (source IN ('facebook', 'whatsapp')) NOT NULL,
  external_id VARCHAR(255) UNIQUE NOT NULL,
  customer_name VARCHAR(255) NOT NULL,
  message_content TEXT NOT NULL,
  timestamp TIMESTAMP WITH TIME ZONE NOT NULL,
  sentiment_score DECIMAL(3, 2), -- -1 to 1
  synced_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

ALTER TABLE conversations_history ENABLE ROW LEVEL SECURITY;

CREATE POLICY "All authenticated users can view conversation history"
  ON conversations_history FOR SELECT
  TO authenticated
  USING (true);

-- ============================================
-- AUTOPILOT ACTIONS TABLE
-- ============================================
CREATE TABLE IF NOT EXISTS autopilot_actions (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  campaign_id UUID REFERENCES campaigns(id) ON DELETE CASCADE,
  action_type VARCHAR(50) CHECK (action_type IN ('increase_budget', 'decrease_budget', 'pause', 'alert')) NOT NULL,
  old_budget DECIMAL(10, 2) NOT NULL,
  new_budget DECIMAL(10, 2) NOT NULL,
  reason TEXT NOT NULL,
  executed_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

ALTER TABLE autopilot_actions ENABLE ROW LEVEL SECURITY;

CREATE POLICY "All authenticated users can view autopilot actions"
  ON autopilot_actions FOR SELECT
  TO authenticated
  USING (true);

-- ============================================
-- NOTIFICATIONS TABLE
-- ============================================
CREATE TABLE IF NOT EXISTS notifications (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  type VARCHAR(50) NOT NULL,
  title VARCHAR(255) NOT NULL,
  message TEXT NOT NULL,
  priority VARCHAR(20) CHECK (priority IN ('low', 'medium', 'high')) DEFAULT 'medium',
  read BOOLEAN DEFAULT FALSE,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

ALTER TABLE notifications ENABLE ROW LEVEL SECURITY;

CREATE POLICY "All authenticated users can view notifications"
  ON notifications FOR SELECT
  TO authenticated
  USING (true);

-- ============================================
-- INDEXES FOR PERFORMANCE
-- ============================================
CREATE INDEX idx_orders_status ON orders(status);
CREATE INDEX idx_orders_created_at ON orders(created_at DESC);
CREATE INDEX idx_leads_status ON leads(status);
CREATE INDEX idx_campaigns_status ON campaigns(status);
CREATE INDEX idx_competitors_last_checked ON competitors(last_checked DESC);
CREATE INDEX idx_competitor_alerts_urgency ON competitor_alerts(urgency);
CREATE INDEX idx_conversations_external_id ON conversations_history(external_id);
CREATE INDEX idx_autopilot_executed_at ON autopilot_actions(executed_at DESC);
CREATE INDEX idx_notifications_read ON notifications(read);

-- ============================================
-- FUNCTIONS
-- ============================================

-- Function to calculate total revenue
CREATE OR REPLACE FUNCTION get_total_revenue()
RETURNS DECIMAL AS $$
  SELECT COALESCE(SUM(total_amount), 0)
  FROM orders
  WHERE status = 'completed';
$$ LANGUAGE SQL STABLE;

-- Function to calculate campaign ROAS
CREATE OR REPLACE FUNCTION calculate_campaign_roas(campaign_id_param UUID)
RETURNS DECIMAL AS $$
  SELECT 
    CASE 
      WHEN total_spend > 0 THEN total_revenue / total_spend
      ELSE 0
    END
  FROM campaigns
  WHERE id = campaign_id_param;
$$ LANGUAGE SQL STABLE;

-- ============================================
-- REALTIME SUBSCRIPTIONS
-- ============================================

-- Enable realtime for critical tables
ALTER PUBLICATION supabase_realtime ADD TABLE orders;
ALTER PUBLICATION supabase_realtime ADD TABLE leads;
ALTER PUBLICATION supabase_realtime ADD TABLE competitor_alerts;
ALTER PUBLICATION supabase_realtime ADD TABLE notifications;

-- ============================================
-- SAMPLE DATA (Optional - for testing)
-- ============================================

-- INSERT INTO campaigns (name, platform, budget, total_spend, total_revenue, status) VALUES
-- ('Facebook Campaign 1', 'facebook', 1000.00, 500.00, 6000.00, 'active'),
-- ('Google Ads Campaign', 'google', 1500.00, 800.00, 2400.00, 'active');

-- INSERT INTO competitors (name, url, current_price, product_name) VALUES
-- ('Competitor A', 'https://competitor-a.com/product', 499.99, 'Premium Widget'),
-- ('Competitor B', 'https://competitor-b.com/product', 549.99, 'Deluxe Widget');
