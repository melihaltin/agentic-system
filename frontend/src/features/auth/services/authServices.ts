import { apiClient } from '@/lib/api'
import { LoginCredentials, RegisterData, UserProfile, BusinessRegistrationData } from '@/types/auth.types'

interface AuthResponse {
  user: any;
  access_token: string;
  refresh_token: string;
  expires_in: number;
}

export class AuthService {
  private token: string | null = null;

  constructor() {
    // Load token from localStorage
    if (typeof window !== 'undefined') {
      this.token = localStorage.getItem('auth_token');
    }
  }

  private saveToken(token: string) {
    this.token = token;
    if (typeof window !== 'undefined') {
      localStorage.setItem('auth_token', token);
    }
  }

  private clearToken() {
    this.token = null;
    if (typeof window !== 'undefined') {
      localStorage.removeItem('auth_token');
    }
  }

  private getAuthHeaders(): Record<string, string> {
    return this.token ? { Authorization: `Bearer ${this.token}` } : {};
  }

  async login(credentials: LoginCredentials): Promise<AuthResponse> {
    console.log('Attempting login with credentials:', credentials);
    
    const response = await apiClient.post<AuthResponse>('/auth/login', credentials);
    
    console.log('Login successful:', response);
    this.saveToken(response.access_token);
    
    return response;
  }

  async register(userData: RegisterData): Promise<AuthResponse> {
    console.log('Attempting registration:', userData);
    
    const response = await apiClient.post<AuthResponse>('/auth/register', userData);
  
    
    console.log('Registration successful:', response);
    this.saveToken(response.access_token);
    
    return response;
  }

  async registerBusiness(businessData: BusinessRegistrationData): Promise<AuthResponse> {
    console.log('Attempting business registration:', businessData);
    
    const response = await apiClient.post<AuthResponse>('/auth/register/business', businessData);
    
    console.log('Business registration successful:', response);
    this.saveToken(response.access_token);
    
    return response;
  }

  async logout(): Promise<void> {
    try {
      if (this.token) {
        await apiClient.post('/auth/logout', {}, this.getAuthHeaders());
      }
    } finally {
      this.clearToken();
    }
  }

  async refreshSession(): Promise<any> {
    const refreshToken = localStorage.getItem('refresh_token');
    if (!refreshToken) {
      throw new Error('No refresh token available');
    }

    const response = await apiClient.post<AuthResponse>('/auth/refresh', { refresh_token: refreshToken });
    
    this.saveToken(response.access_token);
    if (typeof window !== 'undefined') {
      localStorage.setItem('refresh_token', response.refresh_token);
    }
    
    return { session: response, user: response.user };
  }

  async updateProfile(updates: Partial<UserProfile>): Promise<UserProfile> {
    return await apiClient.put<UserProfile>('/auth/profile', updates, this.getAuthHeaders());
  }

  async getProfile(): Promise<UserProfile | null> {
    try {
      if (!this.token) {
        return null;
      }
      
      const profile = await apiClient.get<UserProfile>('/auth/profile', this.getAuthHeaders());
      return profile;
    } catch (error) {
      console.error('Error fetching profile:', error);
      return null;
    }
  }

  async changePassword(newPassword: string): Promise<void> {
    await apiClient.post('/auth/change-password', 
      { current_password: '', new_password: newPassword }, 
      this.getAuthHeaders()
    );
  }

  // For compatibility with existing store
  onAuthStateChange(callback: (event: string, session: any) => void) {
    // This is a simplified implementation
    // In a real app, you might want to implement WebSocket or polling for auth state changes
    return { data: { subscription: { unsubscribe: () => {} } } };
  }

  // Check if user is authenticated
  isAuthenticated(): boolean {
    return !!this.token;
  }

  // Get current user from token (simplified)
  getCurrentUser() {
    return this.token ? { id: 'user-id' } : null;
  }
}

export const authService = new AuthService()