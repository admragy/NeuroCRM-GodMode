/**
 * Auto-Pilot System - Automated Ad Management
 * Automatically adjusts Facebook Ads budget based on ROAS
 * Rules:
 * - ROAS > 10: Increase budget by 20%
 * - ROAS < 2: Pause ad and send report
 */

import { supabase } from '@/lib/supabase/client';

export interface AdCampaign {
  id: string;
  name: string;
  platform: 'facebook' | 'google' | 'tiktok';
  budget: number;
  spend: number;
  revenue: number;
  roas: number; // Return on Ad Spend
  status: 'active' | 'paused' | 'stopped';
  lastOptimized: Date;
}

export interface AutoPilotAction {
  campaignId: string;
  action: 'increase_budget' | 'decrease_budget' | 'pause' | 'alert';
  oldBudget: number;
  newBudget: number;
  reason: string;
  timestamp: Date;
}

/**
 * Calculate ROAS (Return on Ad Spend)
 * ROAS = Revenue / Ad Spend
 */
export function calculateROAS(revenue: number, spend: number): number {
  if (spend === 0) return 0;
  return revenue / spend;
}

/**
 * Auto-Pilot decision engine
 */
export async function evaluateCampaign(
  campaign: AdCampaign
): Promise<AutoPilotAction | null> {
  const roas = calculateROAS(campaign.revenue, campaign.spend);

  // Rule 1: ROAS > 10 → Increase budget by 20%
  if (roas > 10 && campaign.status === 'active') {
    const newBudget = campaign.budget * 1.2;

    return {
      campaignId: campaign.id,
      action: 'increase_budget',
      oldBudget: campaign.budget,
      newBudget,
      reason: `🚀 EXCELLENT ROAS (${roas.toFixed(2)}x)! Increasing budget by 20% to maximize profits.`,
      timestamp: new Date(),
    };
  }

  // Rule 2: ROAS < 2 → Pause ad immediately
  if (roas < 2 && campaign.status === 'active') {
    return {
      campaignId: campaign.id,
      action: 'pause',
      oldBudget: campaign.budget,
      newBudget: 0,
      reason: `⚠️ LOW ROAS (${roas.toFixed(2)}x)! Pausing ad to prevent losses. Review campaign targeting and creative.`,
      timestamp: new Date(),
    };
  }

  // Rule 3: 2 <= ROAS <= 5 → Alert but don't change
  if (roas >= 2 && roas <= 5) {
    return {
      campaignId: campaign.id,
      action: 'alert',
      oldBudget: campaign.budget,
      newBudget: campaign.budget,
      reason: `⚡ MODERATE ROAS (${roas.toFixed(2)}x). Monitor closely. Consider optimizing ad creative or targeting.`,
      timestamp: new Date(),
    };
  }

  // Rule 4: 5 < ROAS < 10 → Gradual increase
  if (roas > 5 && roas < 10 && campaign.status === 'active') {
    const newBudget = campaign.budget * 1.1; // 10% increase

    return {
      campaignId: campaign.id,
      action: 'increase_budget',
      oldBudget: campaign.budget,
      newBudget,
      reason: `✅ GOOD ROAS (${roas.toFixed(2)}x). Increasing budget by 10% for gradual scaling.`,
      timestamp: new Date(),
    };
  }

  return null; // No action needed
}

/**
 * Execute Auto-Pilot action
 */
export async function executeAutoPilotAction(action: AutoPilotAction) {
  const { campaignId, action: actionType, newBudget, reason } = action;

  // Update campaign in database
  if (actionType === 'increase_budget' || actionType === 'decrease_budget') {
    await supabase
      .from('campaigns')
      .update({
        budget: newBudget,
        last_optimized: new Date().toISOString(),
      })
      .eq('id', campaignId);

    // TODO: Call Facebook Ads API to update actual budget
    // await updateFacebookAdBudget(campaignId, newBudget);
  }

  if (actionType === 'pause') {
    await supabase
      .from('campaigns')
      .update({
        status: 'paused',
        last_optimized: new Date().toISOString(),
      })
      .eq('id', campaignId);

    // TODO: Call Facebook Ads API to pause ad
    // await pauseFacebookAd(campaignId);
  }

  // Log action
  await supabase.from('autopilot_actions').insert({
    campaign_id: campaignId,
    action_type: actionType,
    old_budget: action.oldBudget,
    new_budget: newBudget,
    reason,
    executed_at: new Date().toISOString(),
  });

  // Send notification to "Emperor"
  await sendAutoPilotNotification(action);

  console.log(`🤖 Auto-Pilot executed:`, action);
}

/**
 * Send notification to business owner
 */
async function sendAutoPilotNotification(action: AutoPilotAction) {
  await supabase.from('notifications').insert({
    type: 'autopilot_action',
    title: `Auto-Pilot: ${action.action}`,
    message: action.reason,
    priority: action.action === 'pause' ? 'high' : 'medium',
    read: false,
    created_at: new Date().toISOString(),
  });
}

/**
 * Run Auto-Pilot for all campaigns
 */
export async function runAutoPilot() {
  console.log('🤖 Auto-Pilot started...');

  // Get all active campaigns
  const { data: campaigns, error } = await supabase
    .from('campaigns')
    .select('*')
    .in('status', ['active', 'paused']);

  if (error || !campaigns) {
    console.error('Error fetching campaigns:', error);
    return;
  }

  const actions: AutoPilotAction[] = [];

  for (const campaign of campaigns) {
    const action = await evaluateCampaign({
      id: campaign.id,
      name: campaign.name,
      platform: campaign.platform,
      budget: campaign.budget,
      spend: campaign.total_spend || 0,
      revenue: campaign.total_revenue || 0,
      roas: calculateROAS(campaign.total_revenue || 0, campaign.total_spend || 0),
      status: campaign.status,
      lastOptimized: new Date(campaign.last_optimized || Date.now()),
    });

    if (action) {
      actions.push(action);
      await executeAutoPilotAction(action);
    }
  }

  console.log(`✅ Auto-Pilot completed. ${actions.length} actions taken.`);
  return actions;
}

/**
 * Schedule Auto-Pilot to run periodically
 */
export function scheduleAutoPilot(intervalMinutes: number = 30) {
  console.log(`🤖 Auto-Pilot scheduled to run every ${intervalMinutes} minutes`);

  // Run immediately
  runAutoPilot();

  // Schedule periodic runs
  setInterval(runAutoPilot, intervalMinutes * 60 * 1000);
}
