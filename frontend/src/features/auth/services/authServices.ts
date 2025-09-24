import { apiClient } from "@/lib/api";
import {
  LoginCredentials,
  RegisterData,
  UserProfile,
  BusinessRegistrationData,
  ProfileUpdateData,
} from "@/types/auth.types";
import { getSupabaseClient } from "@/lib/supabase/client";
import type { Session, AuthChangeEvent } from "@supabase/supabase-js";

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
    const response = await apiClient.post<AuthResponse>(
      "/auth/login",
      credentials
    );

    // Sync Supabase client session for middleware/cookies
    const supabase = getSupabaseClient();
    await supabase.auth.setSession({
      access_token: response.access_token,
      refresh_token: response.refresh_token,
    });

    this.saveToken(response.access_token);
    if (typeof window !== "undefined") {
      localStorage.setItem("refresh_token", response.refresh_token);
    }
    return response;
  }

  async register(userData: RegisterData): Promise<AuthResponse> {
    const response = await apiClient.post<AuthResponse>(
      "/auth/register",
      userData
    );

    const supabase = getSupabaseClient();
    await supabase.auth.setSession({
      access_token: response.access_token,
      refresh_token: response.refresh_token,
    });

    this.saveToken(response.access_token);
    if (typeof window !== "undefined") {
      localStorage.setItem("refresh_token", response.refresh_token);
    }
    return response;
  }

  async registerBusiness(
    businessData: BusinessRegistrationData
  ): Promise<AuthResponse> {
    const response = await apiClient.post<AuthResponse>(
      "/auth/register/business",
      businessData
    );

    const supabase = getSupabaseClient();
    await supabase.auth.setSession({
      access_token: response.access_token,
      refresh_token: response.refresh_token,
    });

    this.saveToken(response.access_token);
    if (typeof window !== "undefined") {
      localStorage.setItem("refresh_token", response.refresh_token);
    }
    return response;
  }

  async logout(): Promise<void> {
    const supabase = getSupabaseClient();
    await supabase.auth.signOut();
    this.clearToken();
  }

  async refreshSession(): Promise<any> {
    const refreshToken = localStorage.getItem("refresh_token");
    if (!refreshToken) throw new Error("No refresh token available");

    const response = await apiClient.post<AuthResponse>("/auth/refresh", {
      refresh_token: refreshToken,
    });

    const supabase = getSupabaseClient();
    await supabase.auth.setSession({
      access_token: response.access_token,
      refresh_token: response.refresh_token,
    });

    this.saveToken(response.access_token);
    if (typeof window !== "undefined") {
      localStorage.setItem("refresh_token", response.refresh_token);
    }

    return { session: response, user: response.user };
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

  onAuthStateChange(
    callback: (event: AuthChangeEvent, session: Session | null) => void
  ) {
    const supabase = getSupabaseClient();
    const { data } = supabase.auth.onAuthStateChange(
      (event: AuthChangeEvent, session: Session | null) => {
        if (session?.access_token) this.saveToken(session.access_token);
        if (!session) this.clearToken();
        callback(event, session);
      }
    );
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
