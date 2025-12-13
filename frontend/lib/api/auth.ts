import apiClient, { removeAuthToken, setAuthToken } from "../api-client";
import type {
    LoginRequest,
    RegisterRequest,
    User,
    UserWithToken,
} from "../types";

/**
 * Authentication API functions
 */
export const authApi = {
  /**
   * Register a new user
   */
  register: async (data: RegisterRequest): Promise<UserWithToken> => {
    const response = await apiClient.post<UserWithToken>(
      "/api/auth/register",
      data
    );
    
    // Save token to localStorage
    if (response.data.token) {
      setAuthToken(response.data.token);
      // Save user data
      localStorage.setItem("user", JSON.stringify({
        id: response.data.id,
        email: response.data.email,
        full_name: response.data.full_name,
      }));
    }
    
    return response.data;
  },

  /**
   * Login user
   */
  login: async (data: LoginRequest): Promise<UserWithToken> => {
    const response = await apiClient.post<UserWithToken>(
      "/api/auth/login",
      data
    );
    
    // Save token to localStorage
    if (response.data.token) {
      setAuthToken(response.data.token);
      // Save user data
      localStorage.setItem("user", JSON.stringify({
        id: response.data.id,
        email: response.data.email,
        full_name: response.data.full_name,
      }));
    }
    
    return response.data;
  },

  /**
   * Logout user
   */
  logout: async (): Promise<void> => {
    try {
      await apiClient.post("/api/auth/logout");
    } finally {
      // Always remove token, even if API call fails
      removeAuthToken();
    }
  },

  /**
   * Get current user info
   */
  getCurrentUser: async (): Promise<User> => {
    const response = await apiClient.get<User>("/api/auth/me");
    return response.data;
  },

  /**
   * Get user from localStorage (cached)
   */
  getCachedUser: (): User | null => {
    if (typeof window !== "undefined") {
      const userData = localStorage.getItem("user");
      if (userData) {
        try {
          return JSON.parse(userData);
        } catch {
          return null;
        }
      }
    }
    return null;
  },
};
