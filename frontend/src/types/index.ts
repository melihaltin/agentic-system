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
