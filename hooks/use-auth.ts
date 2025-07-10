import { useState, useEffect, useCallback } from "react";

interface User {
  id: string;
  username: string;
  email?: string;
  full_name?: string;
}

interface LoginCredentials {
  username: string;
  password: string;
}

interface AuthResponse {
  access_token: string;
  token_type: string;
}

interface UserResponse {
  username: string;
  email?: string;
  full_name?: string;
}

interface UseAuthReturn {
  user: User | null;
  isLoading: boolean;
  error: string | null;
  login: (credentials: LoginCredentials) => Promise<void>;
  logout: () => void;
  isAuthenticated: boolean;
  fetchUserInfo: () => Promise<void>;
}

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

export const useAuth = (): UseAuthReturn => {
  const [user, setUser] = useState<User | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // Function to fetch user info from backend
  const fetchUserInfo = useCallback(async () => {
    const token = localStorage.getItem("access_token");
    if (!token) return;

    try {
      const response = await fetch(`${API_BASE_URL}/api/auth/me`, {
        headers: {
          Authorization: `Bearer ${token}`,
          "Content-Type": "application/json",
        },
      });

      if (response.ok) {
        const userData: UserResponse = await response.json();
        const user: User = {
          id: userData.username,
          username: userData.username,
          email: userData.email,
          full_name: userData.full_name,
        };
        setUser(user);
        localStorage.setItem("user", JSON.stringify(user));
      } else {
        // Token is invalid, clear storage
        localStorage.removeItem("access_token");
        localStorage.removeItem("user");
        setUser(null);
      }
    } catch (err) {
      console.error("Error fetching user info:", err);
      localStorage.removeItem("access_token");
      localStorage.removeItem("user");
      setUser(null);
    }
  }, []);

  // Check if user is authenticated on mount
  useEffect(() => {
    const token = localStorage.getItem("access_token");
    const userData = localStorage.getItem("user");

    if (token && userData) {
      try {
        const parsedUser = JSON.parse(userData);
        setUser(parsedUser);
        // Fetch fresh user info from backend
        fetchUserInfo();
      } catch (err) {
        console.error("Error parsing user data:", err);
        localStorage.removeItem("access_token");
        localStorage.removeItem("user");
      }
    }
  }, [fetchUserInfo]);

  const login = useCallback(
    async (credentials: LoginCredentials) => {
      setIsLoading(true);
      setError(null);

      try {
        const response = await fetch(`${API_BASE_URL}/api/auth/login`, {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify({
            username: credentials.username,
            password: credentials.password,
          }),
        });

        if (!response.ok) {
          const errorData = await response.json().catch(() => ({}));
          throw new Error(
            errorData.detail || `Login failed: ${response.status}`
          );
        }

        const data: AuthResponse = await response.json();

        // Store token
        localStorage.setItem("access_token", data.access_token);

        // Dispatch custom event to notify token update
        window.dispatchEvent(new CustomEvent("tokenUpdated"));
        console.log("Token stored and event dispatched");

        // Fetch user info from backend
        await fetchUserInfo();
      } catch (err) {
        const errorMessage =
          err instanceof Error ? err.message : "Login failed";
        setError(errorMessage);
        throw err;
      } finally {
        setIsLoading(false);
      }
    },
    [fetchUserInfo]
  );

  const logout = useCallback(() => {
    localStorage.removeItem("access_token");
    localStorage.removeItem("user");
    setUser(null);
    setError(null);

    // Dispatch custom event to notify token removal
    window.dispatchEvent(new CustomEvent("tokenUpdated"));
    console.log("Token removed and event dispatched");
  }, []);

  const isAuthenticated = !!user;

  return {
    user,
    isLoading,
    error,
    login,
    logout,
    isAuthenticated,
    fetchUserInfo,
  };
};

// Hook for user registration
export const useRegister = () => {
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const register = useCallback(
    async (userData: {
      username: string;
      email: string;
      password: string;
      full_name?: string;
    }) => {
      setIsLoading(true);
      setError(null);

      try {
        const response = await fetch(`${API_BASE_URL}/api/auth/register`, {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify(userData),
        });

        if (!response.ok) {
          const errorData = await response.json().catch(() => ({}));
          throw new Error(
            errorData.detail || `Registration failed: ${response.status}`
          );
        }

        const data = await response.json();
        return data;
      } catch (err) {
        const errorMessage =
          err instanceof Error ? err.message : "Registration failed";
        setError(errorMessage);
        throw err;
      } finally {
        setIsLoading(false);
      }
    },
    []
  );

  return {
    register,
    isLoading,
    error,
  };
};

// Hook to get the auth token for API calls - Updated to be reactive
export const useAuthToken = (): string | null => {
  const [token, setToken] = useState<string | null>(null);

  useEffect(() => {
    // Initial token check
    const updateToken = () => {
      const storedToken = localStorage.getItem("access_token");
      console.log("Token updated:", storedToken ? "Present" : "Not found");
      setToken(storedToken);
    };

    updateToken();

    // Listen for storage changes
    const handleStorageChange = (e: StorageEvent) => {
      if (e.key === "access_token") {
        console.log("Storage change detected for access_token");
        updateToken();
      }
    };

    // Listen for custom token update events
    const handleTokenUpdate = () => {
      console.log("Custom token update event received");
      updateToken();
    };

    window.addEventListener("storage", handleStorageChange);
    window.addEventListener("tokenUpdated", handleTokenUpdate);

    // Also check periodically as a fallback
    const interval = setInterval(updateToken, 1000);

    return () => {
      window.removeEventListener("storage", handleStorageChange);
      window.removeEventListener("tokenUpdated", handleTokenUpdate);
      clearInterval(interval);
    };
  }, []);

  return token;
};

// Hook to create authenticated fetch requests
export const useAuthenticatedFetch = () => {
  const authenticatedFetch = useCallback(
    async (url: string, options: RequestInit = {}): Promise<Response> => {
      // Get token fresh each time to ensure it's up to date
      const token = localStorage.getItem("access_token");

      console.log("Making authenticated request to:", url);
      console.log("Token available:", token ? "Yes" : "No");

      const headers: Record<string, string> = {
        "Content-Type": "application/json",
      };

      // Merge existing headers
      if (options.headers) {
        if (
          typeof options.headers === "object" &&
          !Array.isArray(options.headers)
        ) {
          Object.assign(headers, options.headers);
        }
      }

      if (token) {
        headers["Authorization"] = `Bearer ${token}`;
        console.log("Authorization header added");
      } else {
        console.warn("No token available for authenticated request");
      }

      const response = await fetch(url, {
        ...options,
        headers,
      });

      console.log("Response status:", response.status);
      return response;
    },
    []
  );

  return authenticatedFetch;
};
