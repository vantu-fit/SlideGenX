import { useState, useCallback } from "react";
import { useAuthenticatedFetch } from "./use-auth";

interface UseApiOptions<T> {
  onSuccess?: (data: T) => void;
  onError?: (error: string) => void;
}

interface UseApiReturn<T> {
  data: T | null;
  isLoading: boolean;
  error: string | null;
  execute: (...args: any[]) => Promise<void>;
  reset: () => void;
}

export const useApi = <T = any>(
  endpoint: string,
  options: UseApiOptions<T> = {}
): UseApiReturn<T> => {
  const [data, setData] = useState<T | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const authenticatedFetch = useAuthenticatedFetch();

  const execute = useCallback(
    async (...args: any[]) => {
      setIsLoading(true);
      setError(null);

      try {
        const response = await authenticatedFetch(endpoint, ...args);

        if (!response.ok) {
          const errorData = await response.json().catch(() => ({}));
          throw new Error(
            errorData.detail || `HTTP error! status: ${response.status}`
          );
        }

        const result = await response.json();
        setData(result);
        options.onSuccess?.(result);
      } catch (err) {
        const errorMessage =
          err instanceof Error ? err.message : "An error occurred";
        setError(errorMessage);
        options.onError?.(errorMessage);
      } finally {
        setIsLoading(false);
      }
    },
    [endpoint, authenticatedFetch, options]
  );

  const reset = useCallback(() => {
    setData(null);
    setError(null);
    setIsLoading(false);
  }, []);

  return {
    data,
    isLoading,
    error,
    execute,
    reset,
  };
};

// Specific API hooks for common operations
export const useCreateSlide = () => {
  return useApi("/api/slides/create", {
    onSuccess: (data) => {
      console.log("Slide created successfully:", data);
    },
    onError: (error) => {
      console.error("Failed to create slide:", error);
    },
  });
};

export const useGetSlides = () => {
  return useApi("/api/slides", {
    onSuccess: (data) => {
      console.log("Slides fetched successfully:", data);
    },
    onError: (error) => {
      console.error("Failed to fetch slides:", error);
    },
  });
};

export const useUpdateSlide = () => {
  return useApi("/api/slides/update", {
    onSuccess: (data) => {
      console.log("Slide updated successfully:", data);
    },
    onError: (error) => {
      console.error("Failed to update slide:", error);
    },
  });
};

export const useDeleteSlide = () => {
  return useApi("/api/slides/delete", {
    onSuccess: (data) => {
      console.log("Slide deleted successfully:", data);
    },
    onError: (error) => {
      console.error("Failed to delete slide:", error);
    },
  });
};

// User profile hooks
export const useUpdateProfile = () => {
  return useApi("/api/auth/update-profile", {
    onSuccess: (data) => {
      console.log("Profile updated successfully:", data);
    },
    onError: (error) => {
      console.error("Failed to update profile:", error);
    },
  });
};

export const useChangePassword = () => {
  return useApi("/api/auth/change-password", {
    onSuccess: (data) => {
      console.log("Password changed successfully:", data);
    },
    onError: (error) => {
      console.error("Failed to change password:", error);
    },
  });
};
