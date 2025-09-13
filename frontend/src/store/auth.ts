import { create } from "zustand";
import { persist } from "zustand/middleware";
import { AuthState, LoginData, RegisterData, User, Company } from "@/types";

// Mock API functions - replace with real backend calls
const mockApiCall = (data: any, delay = 1000) =>
  new Promise((resolve) => setTimeout(() => resolve(data), delay));

export const useAuthStore = create<AuthState>()(
  persist(
    (set, get) => ({
      user: null,
      company: null,
      isAuthenticated: false,
      isLoading: false,

      login: async (data: LoginData) => {
        set({ isLoading: true });
        try {
          // Mock login - replace with real API call
          await mockApiCall(data);

          const mockUser: User = {
            id: "1",
            email: data.email,
            firstName: "John",
            lastName: "Doe",
            companyId: "1",
          };

          const mockCompany: Company = {
            id: "1",
            name: "Demo Company",
            aiAssistantName: "Demo AI Assistant",
            industry: "Technology",
            website: "https://example.com",
            description: "A demo company for testing",
            createdAt: new Date(),
          };

          set({
            user: mockUser,
            company: mockCompany,
            isAuthenticated: true,
            isLoading: false,
          });
        } catch (error) {
          set({ isLoading: false });
          throw error;
        }
      },

      register: async (data: RegisterData) => {
        set({ isLoading: true });
        try {
          // Mock register - replace with real API call
          await mockApiCall(data, 1500);

          const mockUser: User = {
            id: "1",
            email: data.email,
            firstName: data.firstName,
            lastName: data.lastName,
            companyId: "1",
          };

          const mockCompany: Company = {
            id: "1",
            name: data.companyName,
            aiAssistantName: data.aiAssistantName,
            industry: data.industry,
            website: data.website,
            description: data.description,
            createdAt: new Date(),
          };

          set({
            user: mockUser,
            company: mockCompany,
            isAuthenticated: true,
            isLoading: false,
          });
        } catch (error) {
          set({ isLoading: false });
          throw error;
        }
      },

      logout: () => {
        set({
          user: null,
          company: null,
          isAuthenticated: false,
        });
      },

      updateCompany: async (data: Partial<Company>) => {
        set({ isLoading: true });
        try {
          const currentCompany = get().company;
          if (!currentCompany) throw new Error("No company found");

          // Mock update - replace with real API call
          await mockApiCall(data);

          const updatedCompany = { ...currentCompany, ...data };
          set({
            company: updatedCompany,
            isLoading: false,
          });
        } catch (error) {
          set({ isLoading: false });
          throw error;
        }
      },
    }),
    {
      name: "auth-storage",
      partialize: (state) => ({
        user: state.user,
        company: state.company,
        isAuthenticated: state.isAuthenticated,
      }),
    }
  )
);
