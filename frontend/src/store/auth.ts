import { create } from "zustand";
import { persist } from "zustand/middleware";
import { User } from "@supabase/supabase-js";
import { authService } from "@/features/auth/services/authServices";
import { LoginCredentials, RegisterData, UserProfile, BusinessRegistrationData } from "@/types/auth.types";

export interface AuthStore {
  // State
  user: User | null;
  profile: UserProfile | null;
  loading: boolean;
  initialized: boolean;
  
  // Actions
  login: (credentials: LoginCredentials) => Promise<any>;
  register: (userData: RegisterData) => Promise<any>;
  registerBusiness: (businessData: BusinessRegistrationData) => Promise<any>;
  logout: () => Promise<void>;
  updateProfile: (updates: Partial<UserProfile>) => Promise<void>;
  changePassword: (newPassword: string) => Promise<void>;
  refreshProfile: () => Promise<void>;
  initialize: () => Promise<void>;
  
  // Internal actions
  _setAuthState: (state: Partial<Omit<AuthStore, keyof Actions>>) => void;
}

interface Actions {
  login: AuthStore['login'];
  register: AuthStore['register'];
  registerBusiness: AuthStore['registerBusiness'];
  logout: AuthStore['logout'];
  updateProfile: AuthStore['updateProfile'];
  changePassword: AuthStore['changePassword'];
  refreshProfile: AuthStore['refreshProfile'];
  initialize: AuthStore['initialize'];
  _setAuthState: AuthStore['_setAuthState'];
}

export const useAuthStore = create<AuthStore>()(
  persist(
    (set, get) => ({
      // Initial state
      user: null,
      profile: null,
      loading: true,
      initialized: false,

      // Actions
      login: async (credentials: LoginCredentials) => {
        try {
          set({ loading: true });
          const result = await authService.login(credentials);
          
          // Update user state if login is successful
          if (result?.user) {
            const profile = await authService.getProfile();
            set({
              user: result.user as User,
              profile,
              loading: false,
              initialized: true,
            });
          } else {
            set({ loading: false });
          }
          
          return result;
        } catch (error) {
          set({ loading: false });
          throw error;
        }
      },

      register: async (userData: RegisterData) => {
        try {
          set({ loading: true });

          console.log('Attempting registration with data:', userData);
          const result = await authService.register(userData);
          // Auth state will be updated by the listener in initialize()
          set({ loading: false });
          return result;
        } catch (error) {
          set({ loading: false });
          throw error;
        }
      },

      registerBusiness: async (businessData: BusinessRegistrationData) => {
        try {
          set({ loading: true });
          const result = await authService.registerBusiness(businessData);
          
          // If registration is successful and user is created, update state
          if (result?.user) {
            const profile = await authService.getProfile();
            set({
              user: result.user as User,
              profile,
              loading: false,
              initialized: true,
            });
          } else {
            set({ loading: false });
          }
          
          return result;
        } catch (error) {
          set({ loading: false });
          throw error;
        }
      },

      logout: async () => {
        try {
          set({ loading: true });
          await authService.logout();
          set({
            user: null,
            profile: null,
            loading: false,
            initialized: true,
          });
        } catch (error) {
          set({ loading: false });
          throw error;
        }
      },

      updateProfile: async (updates: Partial<UserProfile>) => {
        try {
          const updatedProfile = await authService.updateProfile(updates);
          set({ profile: updatedProfile });
        } catch (error) {
          throw error;
        }
      },

      changePassword: async (newPassword: string) => {
        try {
          await authService.changePassword(newPassword);
        } catch (error) {
          throw error;
        }
      },

      refreshProfile: async () => {
        try {
          const { user } = get();
          if (user) {
            const profile = await authService.getProfile();
            set({ profile });
          }
        } catch (error) {
          console.error("Error refreshing profile:", error);
        }
      },

      initialize: async () => {
        if (get().initialized) return;

        // Check if user is authenticated
        try {
          if (authService.isAuthenticated()) {
            const profile = await authService.getProfile();
            if (profile) {
              set({
                user: authService.getCurrentUser() as User,
                profile,
                loading: false,
                initialized: true,
              });
            } else {
              // Token exists but profile fetch failed, likely invalid token
              set({
                user: null,
                profile: null,
                loading: false,
                initialized: true,
              });
            }
          } else {
            set({
              user: null,
              profile: null,
              loading: false,
              initialized: true,
            });
          }
        } catch (error) {
          console.error("Error checking authentication:", error);
          set({
            user: null,
            profile: null,
            loading: false,
            initialized: true,
          });
        }

        // Auth state change listener (simplified for backend API)
        const { data: { subscription } } = authService.onAuthStateChange(
          async (event, session) => {
            console.log("Auth state changed:", event, session);
            // This is a no-op for backend API, auth state is managed differently
          }
        );
      },

      // Internal helper for setting state
      _setAuthState: (state) => {
        set(state);
      },
    }),
    {
      name: "auth-storage",
      partialize: (state) => ({
        user: state.user,
        profile: state.profile,
        initialized: state.initialized,
      }),
      onRehydrateStorage: () => (state) => {
        // Initialize auth listener after rehydration
        if (state) {
          state.initialize();
        }
      },
    }
  )
);
