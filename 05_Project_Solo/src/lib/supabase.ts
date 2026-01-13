import { createClient } from '@supabase/supabase-js';

const supabaseUrl = import.meta.env.VITE_SUPABASE_URL;
const supabaseAnonKey = import.meta.env.VITE_SUPABASE_ANON_KEY;

if (!supabaseUrl || !supabaseAnonKey) {
  throw new Error('Missing Supabase environment variables');
}

export const supabase = createClient(supabaseUrl, supabaseAnonKey);

export type Database = {
  public: {
    Tables: {
      users: {
        Row: {
          id: string;
          email: string | null;
          phone: string | null;
          nickname: string | null;
          avatar_url: string | null;
          created_at: string;
          updated_at: string;
        };
        Insert: {
          id: string;
          email?: string | null;
          phone?: string | null;
          nickname?: string | null;
          avatar_url?: string | null;
          created_at?: string;
          updated_at?: string;
        };
        Update: {
          id?: string;
          email?: string | null;
          phone?: string | null;
          nickname?: string | null;
          avatar_url?: string | null;
          created_at?: string;
          updated_at?: string;
        };
      };
      merchants: {
        Row: {
          id: number;
          name: string;
          description: string | null;
          category: string;
          address: string;
          phone: string | null;
          business_hours: string | null;
          latitude: number | null;
          longitude: number | null;
          cover_image: string | null;
          avg_rating: number;
          review_count: number;
          created_at: string;
        };
        Insert: {
          id?: number;
          name: string;
          description?: string | null;
          category: string;
          address: string;
          phone?: string | null;
          business_hours?: string | null;
          latitude?: number | null;
          longitude?: number | null;
          cover_image?: string | null;
          avg_rating?: number;
          review_count?: number;
          created_at?: string;
        };
        Update: {
          id?: number;
          name?: string;
          description?: string | null;
          category?: string;
          address?: string;
          phone?: string | null;
          business_hours?: string | null;
          latitude?: number | null;
          longitude?: number | null;
          cover_image?: string | null;
          avg_rating?: number;
          review_count?: number;
          created_at?: string;
        };
      };
      reviews: {
        Row: {
          id: number;
          user_id: string;
          merchant_id: number;
          rating: number;
          content: string | null;
          images: string[] | null;
          created_at: string;
        };
        Insert: {
          id?: number;
          user_id: string;
          merchant_id: number;
          rating: number;
          content?: string | null;
          images?: string[] | null;
          created_at?: string;
        };
        Update: {
          id?: number;
          user_id?: string;
          merchant_id?: number;
          rating?: number;
          content?: string | null;
          images?: string[] | null;
          created_at?: string;
        };
      };
    };
  };
};
