import axios, { AxiosInstance, AxiosRequestConfig, AxiosResponse } from "axios";

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

class ApiClient {
  private axiosInstance: AxiosInstance;

  constructor(baseURL: string) {
    this.axiosInstance = axios.create({
      baseURL,
      headers: {
        "Content-Type": "application/json",
      },
    });

    // Response interceptor for error handling
    this.axiosInstance.interceptors.response.use(
      (response: AxiosResponse) => response,
      (error) => {
        console.error("API request failed:", error);

        if (error.response?.data) {
          throw new Error(error.response.data.detail || error.message);
        }

        throw error;
      }
    );
  }

  async get<T>(endpoint: string, headers?: Record<string, string>): Promise<T> {
    const config: AxiosRequestConfig = headers ? { headers } : {};
    console.log("🌐 API GET request:", endpoint, "with config:", config);
    const response = await this.axiosInstance.get<T>(endpoint, config);
    return response.data;
  }

  async post<T>(
    endpoint: string,
    data?: any,
    headers?: Record<string, string>
  ): Promise<T> {
    const config: AxiosRequestConfig = headers ? { headers } : {};
    console.log("🌐 API POST request:", endpoint, "with config:", config);
    const response = await this.axiosInstance.post<T>(endpoint, data, config);
    return response.data;
  }

  async put<T>(
    endpoint: string,
    data?: any,
    headers?: Record<string, string>
  ): Promise<T> {
    const config: AxiosRequestConfig = headers ? { headers } : {};
    console.log("🌐 API PUT request:", endpoint, "with config:", config);
    const response = await this.axiosInstance.put<T>(endpoint, data, config);
    return response.data;
  }

  async delete<T>(endpoint: string, config?: AxiosRequestConfig): Promise<T> {
    const response = await this.axiosInstance.delete<T>(endpoint, config);
    return response.data;
  }

  // Additional methods for convenience
  async patch<T>(
    endpoint: string,
    data?: any,
    config?: AxiosRequestConfig
  ): Promise<T> {
    const response = await this.axiosInstance.patch<T>(endpoint, data, config);
    return response.data;
  }

  // Method to set authorization header
  setAuthToken(token: string): void {
    this.axiosInstance.defaults.headers.common[
      "Authorization"
    ] = `Bearer ${token}`;
  }

  // Method to remove authorization header
  removeAuthToken(): void {
    delete this.axiosInstance.defaults.headers.common["Authorization"];
  }
}

export const apiClient = new ApiClient(API_BASE_URL);
