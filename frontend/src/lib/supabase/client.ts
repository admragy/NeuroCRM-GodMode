/**
 * Supabase Client - God Mode Business OS
 * Real-time PostgreSQL connection with Row Level Security
 */

import { createClient } from '@supabase/supabase-js';
import type { Database } from '@/types/database';

const supabaseUrl = process.env.NEXT_PUBLIC_SUPABASE_URL!;
const supabaseAnonKey = process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY!;

if (!supabaseUrl || !supabaseAnonKey) {
  throw new Error('⚠️ Missing Supabase environment variables!');
}

export const supabase = createClient<Database>(supabaseUrl, supabaseAnonKey, {
  auth: {
    persistSession: true,
    autoRefreshToken: true,
    detectSessionInUrl: true,
  },
  realtime: {
    params: {
      eventsPerSecond: 10,
    },
  },
  db: {
    schema: 'public',
  },
});

/**
 * Real-time subscription helper
 * @param table - Table name
 * @param callback - Callback function on data change
 */
export function subscribeToTable<T = any>(
  table: string,
  callback: (payload: { new: T; old: T; eventType: string }) => void
) {
  return supabase
    .channel(`${table}_changes`)
    .on(
      'postgres_changes',
      {
        event: '*',
        schema: 'public',
        table: table,
      },
      (payload: any) => {
        callback(payload);
      }
    )
    .subscribe();
}

/**
 * Real-time revenue counter
 */
export async function getRevenueRealtime() {
  const { data, error } = await supabase
    .from('orders')
    .select('total_amount, status')
    .eq('status', 'completed');

  if (error) throw error;

  return data.reduce((sum, order) => sum + (order.total_amount || 0), 0);
}

/**
 * Real-time orders counter
 */
export async function getOrdersCountRealtime() {
  const { count, error } = await supabase
    .from('orders')
    .select('*', { count: 'exact', head: true });

  if (error) throw error;
  return count || 0;
}

/**
 * Real-time leads counter
 */
export async function getLeadsCountRealtime() {
  const { count, error } = await supabase
    .from('leads')
    .select('*', { count: 'exact', head: true })
    .eq('status', 'new');

  if (error) throw error;
  return count || 0;
}

/**
 * Bulk data sync - The Data Vacuum
 * Syncs historical data from Meta platforms
 */
export async function syncHistoricalData(source: 'facebook' | 'whatsapp', data: any[]) {
  const { data: result, error } = await supabase
    .from('conversations_history')
    .upsert(
      data.map((item) => ({
        source,
        external_id: item.id,
        customer_name: item.name,
        message_content: item.message,
        timestamp: item.timestamp,
        sentiment_score: null, // Will be analyzed by Neuro-Sales Engine
        synced_at: new Date().toISOString(),
      })),
      { onConflict: 'external_id' }
    );

  if (error) throw error;
  return result;
}
