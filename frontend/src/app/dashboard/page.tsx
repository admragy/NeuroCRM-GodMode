'use client';

/**
 * God-Mode Dashboard - Business OS Command Center
 * Real-time operations radar with AI-powered insights
 */

import { useEffect, useState } from 'react';
import { supabase, subscribeToTable, getRevenueRealtime, getOrdersCountRealtime, getLeadsCountRealtime } from '@/lib/supabase/client';
import { analyzeCustomerPsychology } from '@/lib/openai/neuro-sales';
import { runAutoPilot } from '@/lib/automation/auto-pilot';

interface DashboardStats {
  revenue: number;
  orders: number;
  leads: number;
  roas: number;
  conversionRate: number;
}

interface Alert {
  id: string;
  type: 'competitor_price' | 'low_roas' | 'high_roas' | 'new_lead';
  message: string;
  urgency: 'low' | 'medium' | 'high' | 'critical';
  timestamp: Date;
}

export default function GodModeDashboard() {
  const [stats, setStats] = useState<DashboardStats>({
    revenue: 0,
    orders: 0,
    leads: 0,
    roas: 0,
    conversionRate: 0,
  });

  const [alerts, setAlerts] = useState<Alert[]>([]);
  const [autoPilotStatus, setAutoPilotStatus] = useState<'active' | 'paused'>('active');
  const [loading, setLoading] = useState(true);

  // Load real-time stats
  useEffect(() => {
    async function loadStats() {
      try {
        const [revenue, orders, leads] = await Promise.all([
          getRevenueRealtime(),
          getOrdersCountRealtime(),
          getLeadsCountRealtime(),
        ]);

        // Get ROAS from campaigns
        const { data: campaigns } = await supabase
          .from('campaigns')
          .select('total_spend, total_revenue');

        const totalSpend = campaigns?.reduce((sum, c) => sum + (c.total_spend || 0), 0) || 0;
        const totalRevenue = campaigns?.reduce((sum, c) => sum + (c.total_revenue || 0), 0) || 0;
        const roas = totalSpend > 0 ? totalRevenue / totalSpend : 0;

        // Conversion rate
        const conversionRate = orders > 0 && leads > 0 ? (orders / leads) * 100 : 0;

        setStats({
          revenue,
          orders,
          leads,
          roas,
          conversionRate,
        });

        setLoading(false);
      } catch (error) {
        console.error('Error loading stats:', error);
      }
    }

    loadStats();

    // Subscribe to real-time updates
    const ordersSubscription = subscribeToTable('orders', (payload) => {
      if (payload.eventType === 'INSERT') {
        setStats((prev) => ({
          ...prev,
          orders: prev.orders + 1,
          revenue: prev.revenue + (payload.new.total_amount || 0),
        }));
      }
    });

    const leadsSubscription = subscribeToTable('leads', (payload) => {
      if (payload.eventType === 'INSERT') {
        setStats((prev) => ({
          ...prev,
          leads: prev.leads + 1,
        }));

        // Add alert for new lead
        addAlert({
          id: payload.new.id,
          type: 'new_lead',
          message: `New lead: ${payload.new.name}`,
          urgency: 'medium',
          timestamp: new Date(),
        });
      }
    });

    // Subscribe to competitor alerts
    const alertsSubscription = subscribeToTable('competitor_alerts', (payload) => {
      if (payload.eventType === 'INSERT') {
        addAlert({
          id: payload.new.id,
          type: 'competitor_price',
          message: payload.new.message,
          urgency: payload.new.urgency,
          timestamp: new Date(payload.new.created_at),
        });
      }
    });

    return () => {
      ordersSubscription.unsubscribe();
      leadsSubscription.unsubscribe();
      alertsSubscription.unsubscribe();
    };
  }, []);

  // Auto-Pilot monitor
  useEffect(() => {
    if (autoPilotStatus === 'active') {
      // Run every 30 minutes
      const interval = setInterval(() => {
        runAutoPilot();
      }, 30 * 60 * 1000);

      return () => clearInterval(interval);
    }
  }, [autoPilotStatus]);

  function addAlert(alert: Alert) {
    setAlerts((prev) => [alert, ...prev].slice(0, 10)); // Keep last 10 alerts
  }

  const getAlertColor = (urgency: Alert['urgency']) => {
    switch (urgency) {
      case 'critical':
        return 'bg-red-500/20 border-red-500 text-red-400';
      case 'high':
        return 'bg-orange-500/20 border-orange-500 text-orange-400';
      case 'medium':
        return 'bg-yellow-500/20 border-yellow-500 text-yellow-400';
      case 'low':
        return 'bg-blue-500/20 border-blue-500 text-blue-400';
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-black flex items-center justify-center">
        <div className="text-green-400 text-2xl font-mono animate-pulse">
          ⚡ INITIALIZING GOD MODE...
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-black via-gray-900 to-black text-white p-8">
      {/* Header */}
      <header className="mb-12">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-5xl font-black text-transparent bg-clip-text bg-gradient-to-r from-green-400 to-blue-500 mb-2">
              ⚡ GOD MODE BUSINESS OS
            </h1>
            <p className="text-gray-400 font-mono text-sm">
              OmniCRM Ultimate v7.1.0 - Emperor Dashboard
            </p>
          </div>

          {/* Auto-Pilot Status */}
          <div className="flex items-center gap-4">
            <div
              className={`px-6 py-3 rounded-lg border-2 ${
                autoPilotStatus === 'active'
                  ? 'bg-green-500/20 border-green-500 text-green-400'
                  : 'bg-gray-500/20 border-gray-500 text-gray-400'
              }`}
            >
              <div className="flex items-center gap-2">
                <div
                  className={`w-3 h-3 rounded-full ${
                    autoPilotStatus === 'active' ? 'bg-green-400 animate-pulse' : 'bg-gray-400'
                  }`}
                />
                <span className="font-mono font-bold">
                  AUTO-PILOT: {autoPilotStatus.toUpperCase()}
                </span>
              </div>
            </div>

            <button
              onClick={() =>
                setAutoPilotStatus((prev) => (prev === 'active' ? 'paused' : 'active'))
              }
              className="px-6 py-3 bg-blue-600 hover:bg-blue-700 rounded-lg font-bold transition-all"
            >
              {autoPilotStatus === 'active' ? '⏸ PAUSE' : '▶ ACTIVATE'}
            </button>
          </div>
        </div>
      </header>

      {/* Stats Grid */}
      <div className="grid grid-cols-1 md:grid-cols-5 gap-6 mb-12">
        {/* Revenue */}
        <div className="bg-gradient-to-br from-green-500/10 to-green-500/5 border-2 border-green-500/30 rounded-xl p-6">
          <div className="text-green-400 text-sm font-mono mb-2">TOTAL REVENUE</div>
          <div className="text-4xl font-black text-white mb-1">
            ${stats.revenue.toLocaleString()}
          </div>
          <div className="text-xs text-green-300">+12.5% from last week</div>
        </div>

        {/* Orders */}
        <div className="bg-gradient-to-br from-blue-500/10 to-blue-500/5 border-2 border-blue-500/30 rounded-xl p-6">
          <div className="text-blue-400 text-sm font-mono mb-2">ORDERS</div>
          <div className="text-4xl font-black text-white mb-1">{stats.orders}</div>
          <div className="text-xs text-blue-300">Real-time count</div>
        </div>

        {/* Leads */}
        <div className="bg-gradient-to-br from-purple-500/10 to-purple-500/5 border-2 border-purple-500/30 rounded-xl p-6">
          <div className="text-purple-400 text-sm font-mono mb-2">NEW LEADS</div>
          <div className="text-4xl font-black text-white mb-1">{stats.leads}</div>
          <div className="text-xs text-purple-300">Awaiting contact</div>
        </div>

        {/* ROAS */}
        <div className="bg-gradient-to-br from-yellow-500/10 to-yellow-500/5 border-2 border-yellow-500/30 rounded-xl p-6">
          <div className="text-yellow-400 text-sm font-mono mb-2">ROAS</div>
          <div className="text-4xl font-black text-white mb-1">
            {stats.roas.toFixed(1)}x
          </div>
          <div className="text-xs text-yellow-300">
            {stats.roas > 10 ? '🚀 EXCELLENT' : stats.roas > 5 ? '✅ GOOD' : '⚠️ LOW'}
          </div>
        </div>

        {/* Conversion Rate */}
        <div className="bg-gradient-to-br from-red-500/10 to-red-500/5 border-2 border-red-500/30 rounded-xl p-6">
          <div className="text-red-400 text-sm font-mono mb-2">CONVERSION</div>
          <div className="text-4xl font-black text-white mb-1">
            {stats.conversionRate.toFixed(1)}%
          </div>
          <div className="text-xs text-red-300">Leads → Orders</div>
        </div>
      </div>

      {/* Alerts Section */}
      <div className="mb-12">
        <h2 className="text-2xl font-black mb-6 text-gray-100">
          🚨 LIVE ALERTS & NOTIFICATIONS
        </h2>

        <div className="space-y-3">
          {alerts.length === 0 ? (
            <div className="bg-gray-800/50 border border-gray-700 rounded-lg p-6 text-center text-gray-400">
              All systems operational. No alerts at this time.
            </div>
          ) : (
            alerts.map((alert) => (
              <div
                key={alert.id}
                className={`border-2 rounded-lg p-4 ${getAlertColor(alert.urgency)}`}
              >
                <div className="flex items-start justify-between">
                  <div className="flex-1">
                    <div className="font-mono text-xs mb-1 opacity-70">
                      {alert.type.toUpperCase().replace('_', ' ')} -{' '}
                      {alert.timestamp.toLocaleTimeString()}
                    </div>
                    <div className="font-bold">{alert.message}</div>
                  </div>
                  <button className="text-xs opacity-50 hover:opacity-100">✕</button>
                </div>
              </div>
            ))
          )}
        </div>
      </div>

      {/* Action Buttons */}
      <div className="grid grid-cols-3 gap-4">
        <button className="bg-gradient-to-r from-green-600 to-green-700 hover:from-green-700 hover:to-green-800 p-6 rounded-xl font-black text-xl transition-all border-2 border-green-500">
          🎯 NEURO-SALES ENGINE
        </button>
        <button className="bg-gradient-to-r from-red-600 to-red-700 hover:from-red-700 hover:to-red-800 p-6 rounded-xl font-black text-xl transition-all border-2 border-red-500">
          📡 COMPETITOR RADAR
        </button>
        <button className="bg-gradient-to-r from-purple-600 to-purple-700 hover:from-purple-700 hover:to-purple-800 p-6 rounded-xl font-black text-xl transition-all border-2 border-purple-500">
          🤖 AUTO-PILOT CONTROL
        </button>
      </div>
    </div>
  );
}
