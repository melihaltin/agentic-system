export interface User {
  id: string;
  email: string;
  firstName: string;
  lastName: string;
  companyId: string;
}

export interface Company {
  id: string;
  name: string;
  aiAssistantName: string;
  industry?: string;
  website?: string;
  description?: string;
  createdAt: Date;
}

export interface RegisterData {
  // User info
  firstName: string;
  lastName: string;
  email: string;
  password: string;
  // Company info
  companyName: string;
  aiAssistantName: string;
  industry?: string;
  website?: string;
  description?: string;
}

export type BusinessCategory =
  | "e-commerce"
  | "car-rental"
  | "restaurant"
  | "service-based";

export type PlatformType = {
  "e-commerce":
    | "shopify"
    | "woocommerce"
    | "magento"
    | "bigcommerce"
    | "custom";
  "car-rental": "turo" | "getaround" | "zipcar" | "custom";
  restaurant: "ubereats" | "doordash" | "grubhub" | "custom";
  "service-based": "calendly" | "square" | "stripe" | "custom";
};

export interface BusinessRegistrationData {
  // Step 1: Basic Info
  businessName: string;
  phoneNumber: string;
  email: string;

  // Step 2: Category
  category: BusinessCategory | "";

  // Step 3: Platform
  platform: string;

  // Step 4: API Configuration
  apiKey: string;
  apiSecret?: string;
  additionalConfig?: Record<string, string>;
}

export interface BusinessRegistrationErrors {
  businessName?: string;
  phoneNumber?: string;
  email?: string;
  category?: string;
  platform?: string;
  apiKey?: string;
  apiSecret?: string;
}

export interface BusinessRegistrationStep {
  id: number;
  title: string;
  description: string;
  isCompleted: boolean;
  isActive: boolean;
}

export interface LoginData {
  email: string;
  password: string;
}

export interface AuthState {
  user: User | null;
  company: Company | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  login: (data: LoginData) => Promise<void>;
  register: (data: RegisterData) => Promise<void>;
  logout: () => void;
  updateCompany: (data: Partial<Company>) => Promise<void>;
}
