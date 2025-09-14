import { User } from "@supabase/supabase-js"

export interface CompanyProfile {
  id: string
  user_id: string
  company_name: string
  phone_number: string
  business_category: string
  platform: string
  api_key?: string
  api_secret?: string
  additional_config?: Record<string, any>
  created_at: string
  updated_at: string
}

export interface UserProfile {
  id: string
  email: string
  full_name?: string
  avatar_url?: string
  role: 'user' | 'admin'
  created_at: string
  updated_at: string
  company?: CompanyProfile
}

export interface AuthState {
  user: User | null
  profile: UserProfile | null
  loading: boolean
  initialized: boolean
}

export interface LoginCredentials {
  email: string
  password: string
}

export interface RegisterData {
  email: string
  password: string
  full_name?: string
}

export interface BusinessRegistrationData {
  email: string
  password: string
  full_name: string
  company_name: string
  phone_number: string
  business_category: string
  platform: string
  api_key?: string
  api_secret?: string
  additional_config?: Record<string, any>
}

export interface AuthResponse {
  user: User
  access_token: string
  refresh_token: string
  expires_in: number
}