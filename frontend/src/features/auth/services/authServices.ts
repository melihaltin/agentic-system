import { apiClient } from "@/lib/api";
import {
  LoginCredentials,
  RegisterData,
  UserProfile,
  BusinessRegistrationData,
  ProfileUpdateData,
} from "@/types/auth.types";
import { getSupabaseClient } from "@/lib/supabase/client";

interface AuthResponse {
  user: any;
  access_token: string;
  refresh_token: string;
  expires_in: number;
}

export class AuthService {
  private token: string | null = null;

  constructor() {
    if (typeof window !== "undefined") {
      this.token = localStorage.getItem("auth_token");
    }
  }

  private saveToken(token: string) {
    this.token = token;
    if (typeof window !== "undefined") {
      localStorage.setItem("auth_token", token);
    }
  }

  private clearToken() {
    this.token = null;
    if (typeof window !== "undefined") {
      localStorage.removeItem("auth_token");
      localStorage.removeItem("refresh_token");
    }
  }

  private getAuthHeaders(): Record<string, string> {
    return this.token ? { Authorization: `Bearer ${this.token}` } : {};
  }

  async login(credentials: LoginCredentials): Promise<AuthResponse> {
    const supabase = getSupabaseClient();
    const { data, error } = await supabase.auth.signInWithPassword({
      email: credentials.email,
      password: credentials.password,
    });
    if (error || !data.session) throw error || new Error("Login failed");

    const { session, user } = data;
    this.saveToken(session.access_token);
    if (typeof window !== "undefined") {
      localStorage.setItem("refresh_token", session.refresh_token);
    }

    return {
      user,
      access_token: session.access_token,
      refresh_token: session.refresh_token,
      expires_in: session.expires_in ?? 3600,
    };
  }

  async register(userData: RegisterData): Promise<AuthResponse> {
    const supabase = getSupabaseClient();
    const { data, error } = await supabase.auth.signUp({
      email: userData.email,
      password: userData.password,
      options: {
        data: { full_name: userData.full_name },
      },
    });
    if (error || !data.session || !data.user)
      throw error || new Error("Registration failed");

    const { session, user } = data;
    this.saveToken(session.access_token);
    if (typeof window !== "undefined") {
      localStorage.setItem("refresh_token", session.refresh_token);
    }

    return {
      user,
      access_token: session.access_token,
      refresh_token: session.refresh_token,
      expires_in: session.expires_in ?? 3600,
    };
  }

  async registerBusiness(
    businessData: BusinessRegistrationData
  ): Promise<AuthResponse> {
    // Create auth user
    const supabase = getSupabaseClient();
    const { data, error } = await supabase.auth.signUp({
      email: businessData.email,
      password: businessData.password,
      options: {
        data: { full_name: businessData.full_name },
      },
    });
    if (error || !data.session || !data.user)
      throw error || new Error("Business registration failed");

    const { session, user } = data;
    this.saveToken(session.access_token);
    if (typeof window !== "undefined") {
      localStorage.setItem("refresh_token", session.refresh_token);
    }

    // Optionally call backend to create company_profile row to keep schema consistent
    try {
      await apiClient.post(
        "/auth/register/business",
        businessData,
        this.getAuthHeaders()
      );
    } catch (_) {}

    return {
      user,
      access_token: session.access_token,
      refresh_token: session.refresh_token,
      expires_in: session.expires_in ?? 3600,
    };
  }

  async logout(): Promise<void> {
    const supabase = getSupabaseClient();
    await supabase.auth.signOut();
    this.clearToken();
  }

  async refreshSession(): Promise<any> {
    const supabase = getSupabaseClient();
    const { data, error } = await supabase.auth.refreshSession();
    if (error || !data.session)
      throw error || new Error("No refresh token available");

    const { session, user } = data;
    this.saveToken(session.access_token);
    if (typeof window !== "undefined") {
      localStorage.setItem("refresh_token", session.refresh_token);
    }
    return { session, user };
  }

  async updateProfile(updates: ProfileUpdateData): Promise<UserProfile> {
    return await apiClient.put<UserProfile>(
      "/auth/profile",
      updates,
      this.getAuthHeaders()
    );
  }

  async getProfile(): Promise<UserProfile | null> {
    try {
      if (!this.token) return null;
      const profile = await apiClient.get<UserProfile>(
        "/auth/profile",
        this.getAuthHeaders()
      );
      return profile;
    } catch (error) {
      console.error("❌ Error fetching profile:", error);
      return null;
    }
  }

  async changePassword(newPassword: string): Promise<void> {
    const supabase = getSupabaseClient();
    const { error } = await supabase.auth.updateUser({ password: newPassword });
    if (error) throw error;
  }

  onAuthStateChange(callback: (event: string, session: any) => void) {
    const supabase = getSupabaseClient();
    const { data } = supabase.auth.onAuthStateChange((event: string, session: { access_token: string; }) => {
      // Keep local token in sync for header-based backend calls
      if (session?.access_token) this.saveToken(session.access_token);
      if (!session) this.clearToken();
      callback(event, session);
    });
    return { data };
  }

  isAuthenticated(): boolean {
    return !!this.token;
  }

  getCurrentUser() {
    return this.token ? { id: "user-id" } : null;
  }
}

export const authService = new AuthService();
