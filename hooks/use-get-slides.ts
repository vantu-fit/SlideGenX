import { useState, useCallback, useEffect } from "react";
import { useAuthenticatedFetch } from "./use-auth";

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

// Types
interface UseGetSlideIdsReturn {
  slideIds: string[];
  isLoading: boolean;
  error: string | null;
  fetchSlideIds: () => Promise<string[]>;
  reset: () => void;
}

interface UseGetSlideBySessionIdReturn {
  downloadSlide: (sessionId: string, fileName?: string) => Promise<void>;
  isLoading: boolean;
  error: string | null;
  reset: () => void;
}

interface SlideDetail {
  slide_index: number;
  title: string;
  content: string | string[];
  notes: string;
  keywords: string[];
  has_images: boolean;
  has_diagrams: boolean;
  section_index: number;
  slide_index_in_section: number;
}

interface SlideInfo {
  session_id: string;
  title: string;
  num_slides: number;
  template: string | null;
  created_at: number | null;
  slide_details: SlideDetail[];
  outline: any;
  user_input: any;
}

interface UseGetSlideInfoReturn {
  slideInfo: SlideInfo | null;
  isLoading: boolean;
  error: string | null;
  fetchSlideInfo: (sessionId: string) => Promise<SlideInfo>;
  reset: () => void;
}

interface UseSlideManagementReturn {
  slideIds: string[];
  isLoadingIds: boolean;
  errorIds: string | null;
  downloadSlide: (sessionId: string, fileName?: string) => Promise<void>;
  isDownloading: boolean;
  errorDownload: string | null;
  fetchSlideIds: () => Promise<string[]>;
  resetIds: () => void;
  resetDownload: () => void;
}

/**
 * Hook để lấy danh sách session IDs của slides đã tạo
 * API: GET /api/slide/get_slide_ids
 */
export const useGetSlideIds = (): UseGetSlideIdsReturn => {
  const [slideIds, setSlideIds] = useState<string[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const authenticatedFetch = useAuthenticatedFetch();

  const fetchSlideIds = useCallback(async (): Promise<string[]> => {
    setIsLoading(true);
    setError(null);

    try {
      const response = await authenticatedFetch(
        `${API_BASE_URL}/api/slide/get_slide_ids`,
        {
          method: "GET",
        }
      );

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        throw new Error(
          errorData.detail || `Lỗi lấy danh sách slides: ${response.status}`
        );
      }

      const result: string[] = await response.json();
      setSlideIds(result);
      console.log("Slide IDs fetched successfully:", result);
      return result;
    } catch (err) {
      const errorMessage =
        err instanceof Error ? err.message : "Lỗi lấy danh sách slides";
      setError(errorMessage);
      console.error("Error fetching slide IDs:", err);
      throw err;
    } finally {
      setIsLoading(false);
    }
  }, [authenticatedFetch]);

  const reset = useCallback(() => {
    setSlideIds([]);
    setError(null);
    setIsLoading(false);
  }, []);

  return {
    slideIds,
    isLoading,
    error,
    fetchSlideIds,
    reset,
  };
};

/**
 * Hook để lấy thông tin chi tiết slide từ memory.json
 * API: GET /api/slide/get_slide_info/{session_id}
 */
export const useGetSlideInfo = (): UseGetSlideInfoReturn => {
  const [slideInfo, setSlideInfo] = useState<SlideInfo | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const authenticatedFetch = useAuthenticatedFetch();

  const fetchSlideInfo = useCallback(
    async (sessionId: string): Promise<SlideInfo> => {
      console.log("fetchSlideInfo called with sessionId:", sessionId);

      // Check if token exists before making request
      const token = localStorage.getItem("access_token");
      if (!token) {
        const errorMessage = "No authentication token available";
        console.error(errorMessage);
        setError(errorMessage);
        throw new Error(errorMessage);
      }

      console.log("Authentication token found, proceeding with request");
      setIsLoading(true);
      setError(null);

      try {
        const url = `${API_BASE_URL}/api/slide/get_slide_info/${sessionId}`;
        console.log("Making request to:", url);

        const response = await authenticatedFetch(url, {
          method: "GET",
        });

        console.log("Response received:", response.status, response.statusText);

        if (!response.ok) {
          const errorData = await response.json().catch(() => ({}));
          console.error("API error response:", errorData);

          const errorMessage =
            errorData.detail || `Lỗi lấy thông tin slide: ${response.status}`;
          setError(errorMessage);
          throw new Error(errorMessage);
        }

        const result: SlideInfo = await response.json();
        console.log("Slide info fetched successfully:", result);
        setSlideInfo(result);
        return result;
      } catch (err) {
        const errorMessage =
          err instanceof Error ? err.message : "Lỗi lấy thông tin slide";
        console.error("Error in fetchSlideInfo:", err);
        setError(errorMessage);
        throw err;
      } finally {
        setIsLoading(false);
      }
    },
    [authenticatedFetch]
  );

  const reset = useCallback(() => {
    setSlideInfo(null);
    setError(null);
    setIsLoading(false);
  }, []);

  return {
    slideInfo,
    isLoading,
    error,
    fetchSlideInfo,
    reset,
  };
};

/**
 * Hook để download slide bằng session ID
 * API: GET /api/slide/get_slide_by_session_id/{session_id}
 */
export const useGetSlideBySessionId = (): UseGetSlideBySessionIdReturn => {
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const authenticatedFetch = useAuthenticatedFetch();

  const downloadSlide = useCallback(
    async (sessionId: string, fileName?: string) => {
      setIsLoading(true);
      setError(null);

      try {
        const response = await authenticatedFetch(
          `${API_BASE_URL}/api/slide/get_slide_by_session_id/${sessionId}`,
          {
            method: "GET",
          }
        );

        if (!response.ok) {
          const errorData = await response.json().catch(() => ({}));
          throw new Error(
            errorData.detail || `Lỗi download slide: ${response.status}`
          );
        }

        // Tạo blob từ response và download file PPTX
        const blob = await response.blob();
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement("a");
        a.href = url;
        a.download = fileName || `slide_${sessionId}.pptx`;
        document.body.appendChild(a);
        a.click();
        window.URL.revokeObjectURL(url);
        document.body.removeChild(a);

        console.log("Slide downloaded successfully:", sessionId);
      } catch (err) {
        const errorMessage =
          err instanceof Error ? err.message : "Lỗi download slide";
        setError(errorMessage);
        console.error("Error downloading slide:", err);
        throw err;
      } finally {
        setIsLoading(false);
      }
    },
    [authenticatedFetch]
  );

  const reset = useCallback(() => {
    setError(null);
    setIsLoading(false);
  }, []);

  return {
    downloadSlide,
    isLoading,
    error,
    reset,
  };
};

/**
 * Hook tổng hợp để quản lý slides
 * Kết hợp cả hai hooks trên
 */
export const useSlideManagement = (): UseSlideManagementReturn => {
  const {
    slideIds,
    isLoading: isLoadingIds,
    error: errorIds,
    fetchSlideIds,
    reset: resetIds,
  } = useGetSlideIds();

  const {
    downloadSlide,
    isLoading: isDownloading,
    error: errorDownload,
    reset: resetDownload,
  } = useGetSlideBySessionId();

  return {
    slideIds,
    isLoadingIds,
    errorIds,
    downloadSlide,
    isDownloading,
    errorDownload,
    fetchSlideIds,
    resetIds,
    resetDownload,
  };
};

/**
 * Hook với auto-fetch khi component mount
 */
export const useSlideManagementWithAutoFetch = (): UseSlideManagementReturn => {
  const slideManagement = useSlideManagement();

  useEffect(() => {
    // Auto fetch slide IDs khi component mount
    slideManagement.fetchSlideIds().catch((error) => {
      console.error("Auto fetch slides failed:", error);
    });
  }, []);

  return slideManagement;
};

// Utility functions
export const hasSlides = (slideIds: string[]): boolean => {
  return slideIds.length > 0;
};

export const getSlideCount = (slideIds: string[]): number => {
  return slideIds.length;
};

export const isValidSessionId = (sessionId: string): boolean => {
  // Basic UUID validation
  const uuidRegex =
    /^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$/i;
  return uuidRegex.test(sessionId);
};

// Helper functions for slide info
export const formatSlideCreatedDate = (timestamp: number | null): string => {
  if (!timestamp) return "Unknown";
  return new Date(timestamp * 1000).toLocaleDateString("vi-VN", {
    year: "numeric",
    month: "long",
    day: "numeric",
    hour: "2-digit",
    minute: "2-digit",
  });
};

export const getSlideImageUrl = (
  sessionId: string,
  slideIndex: number
): string => {
  return `${API_BASE_URL}/image/${sessionId}/images/page_${slideIndex + 1}.png`;
};
