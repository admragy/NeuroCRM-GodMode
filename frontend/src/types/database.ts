/**
 * Supabase Database Types - Auto-generated
 */

export type Json =
  | string
  | number
  | boolean
  | null
  | { [key: string]: Json | undefined }
  | Json[]

export interface Database {
  public: {
    Tables: {
      orders: {
        Row: {
          id: string
          customer_id: string | null
          total_amount: number
          status: 'pending' | 'completed' | 'cancelled'
          created_at: string
        }
        Insert: {
          id?: string
          customer_id?: string | null
          total_amount: number
          status?: 'pending' | 'completed' | 'cancelled'
          created_at?: string
        }
        Update: {
          id?: string
          customer_id?: string | null
          total_amount?: number
          status?: 'pending' | 'completed' | 'cancelled'
          created_at?: string
        }
      }
      leads: {
        Row: {
          id: string
          name: string
          phone: string | null
          email: string | null
          status: 'new' | 'contacted' | 'converted' | 'lost'
          source: string | null
          psycho_profile: string | null
          created_at: string
        }
        Insert: {
          id?: string
          name: string
          phone?: string | null
          email?: string | null
          status?: 'new' | 'contacted' | 'converted' | 'lost'
          source?: string | null
          psycho_profile?: string | null
          created_at?: string
        }
        Update: {
          id?: string
          name?: string
          phone?: string | null
          email?: string | null
          status?: 'new' | 'contacted' | 'converted' | 'lost'
          source?: string | null
          psycho_profile?: string | null
          created_at?: string
        }
      }
      campaigns: {
        Row: {
          id: string
          name: string
          platform: 'facebook' | 'google' | 'tiktok'
          budget: number
          total_spend: number | null
          total_revenue: number | null
          status: 'active' | 'paused' | 'stopped'
          last_optimized: string | null
          created_at: string
        }
        Insert: {
          id?: string
          name: string
          platform: 'facebook' | 'google' | 'tiktok'
          budget: number
          total_spend?: number | null
          total_revenue?: number | null
          status?: 'active' | 'paused' | 'stopped'
          last_optimized?: string | null
          created_at?: string
        }
        Update: {
          id?: string
          name?: string
          platform?: 'facebook' | 'google' | 'tiktok'
          budget?: number
          total_spend?: number | null
          total_revenue?: number | null
          status?: 'active' | 'paused' | 'stopped'
          last_optimized?: string | null
          created_at?: string
        }
      }
      competitors: {
        Row: {
          id: string
          name: string
          url: string
          current_price: number
          previous_price: number
          price_change_percentage: number
          product_name: string
          stock_status: 'in_stock' | 'out_of_stock' | 'low_stock'
          promo_text: string | null
          last_checked: string
        }
        Insert: {
          id?: string
          name: string
          url: string
          current_price: number
          previous_price?: number
          price_change_percentage?: number
          product_name: string
          stock_status?: 'in_stock' | 'out_of_stock' | 'low_stock'
          promo_text?: string | null
          last_checked?: string
        }
        Update: {
          id?: string
          name?: string
          url?: string
          current_price?: number
          previous_price?: number
          price_change_percentage?: number
          product_name?: string
          stock_status?: 'in_stock' | 'out_of_stock' | 'low_stock'
          promo_text?: string | null
          last_checked?: string
        }
      }
      competitor_alerts: {
        Row: {
          id: string
          competitor_id: string
          alert_type: string
          message: string
          urgency: 'low' | 'medium' | 'high' | 'critical'
          suggested_action: Json | null
          created_at: string
        }
        Insert: {
          id?: string
          competitor_id: string
          alert_type: string
          message: string
          urgency: 'low' | 'medium' | 'high' | 'critical'
          suggested_action?: Json | null
          created_at?: string
        }
        Update: {
          id?: string
          competitor_id?: string
          alert_type?: string
          message?: string
          urgency?: 'low' | 'medium' | 'high' | 'critical'
          suggested_action?: Json | null
          created_at?: string
        }
      }
      conversations_history: {
        Row: {
          id: string
          source: 'facebook' | 'whatsapp'
          external_id: string
          customer_name: string
          message_content: string
          timestamp: string
          sentiment_score: number | null
          synced_at: string
        }
        Insert: {
          id?: string
          source: 'facebook' | 'whatsapp'
          external_id: string
          customer_name: string
          message_content: string
          timestamp: string
          sentiment_score?: number | null
          synced_at?: string
        }
        Update: {
          id?: string
          source?: 'facebook' | 'whatsapp'
          external_id?: string
          customer_name?: string
          message_content?: string
          timestamp?: string
          sentiment_score?: number | null
          synced_at?: string
        }
      }
      autopilot_actions: {
        Row: {
          id: string
          campaign_id: string
          action_type: 'increase_budget' | 'decrease_budget' | 'pause' | 'alert'
          old_budget: number
          new_budget: number
          reason: string
          executed_at: string
        }
        Insert: {
          id?: string
          campaign_id: string
          action_type: 'increase_budget' | 'decrease_budget' | 'pause' | 'alert'
          old_budget: number
          new_budget: number
          reason: string
          executed_at?: string
        }
        Update: {
          id?: string
          campaign_id?: string
          action_type?: 'increase_budget' | 'decrease_budget' | 'pause' | 'alert'
          old_budget?: number
          new_budget?: number
          reason?: string
          executed_at?: string
        }
      }
      notifications: {
        Row: {
          id: string
          type: string
          title: string
          message: string
          priority: 'low' | 'medium' | 'high'
          read: boolean
          created_at: string
        }
        Insert: {
          id?: string
          type: string
          title: string
          message: string
          priority?: 'low' | 'medium' | 'high'
          read?: boolean
          created_at?: string
        }
        Update: {
          id?: string
          type?: string
          title?: string
          message?: string
          priority?: 'low' | 'medium' | 'high'
          read?: boolean
          created_at?: string
        }
      }
    }
    Views: {
      [_ in never]: never
    }
    Functions: {
      [_ in never]: never
    }
    Enums: {
      [_ in never]: never
    }
  }
}
