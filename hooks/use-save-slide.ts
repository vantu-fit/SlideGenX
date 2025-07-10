import { useState } from "react";
import { useAuthenticatedFetch } from "./use-auth";

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

// Types
interface SaveSlideRequest {
  session_id: string;
}

interface SaveSlideResponse {
  id: number;
  session_id: string;
  user_id: string;
}

interface UseSaveSlideReturn {
  saveSlide: (sessionId: string) => Promise<SaveSlideResponse>;
  isLoading: boolean;
  error: string | null;
  response: SaveSlideResponse | null;
  reset: () => void;
}

/**
 * Hook để save slide vào database
 * API yêu cầu authentication và nhận session_id
 */
export const useSaveSlide = (): UseSaveSlideReturn => {
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [response, setResponse] = useState<SaveSlideResponse | null>(null);

  const authenticatedFetch = useAuthenticatedFetch();

  const saveSlide = async (sessionId: string): Promise<SaveSlideResponse> => {
    setIsLoading(true);
    setError(null);

    try {
      const response = await authenticatedFetch(
        `${API_BASE_URL}/api/slide/save_slide`,
        {
          method: "POST",
          body: JSON.stringify({ session_id: sessionId }),
        }
      );

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        throw new Error(
          errorData.detail || `Lỗi lưu slide: ${response.status}`
        );
      }

      const result: SaveSlideResponse = await response.json();
      setResponse(result);
      console.log("Slide saved successfully:", result);
      return result;
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : "Lỗi lưu slide";
      setError(errorMessage);
      console.error("Error saving slide:", err);
      throw err;
    } finally {
      setIsLoading(false);
    }
  };

  const reset = () => {
    setResponse(null);
    setError(null);
    setIsLoading(false);
  };

  return {
    saveSlide,
    isLoading,
    error,
    response,
    reset,
  };
};

/**
 * Hook tổng hợp để tạo và lưu slide
 * Kết hợp generate slide và save slide
 */
export const useSlideWorkflow = () => {
  const [currentStep, setCurrentStep] = useState<
    "idle" | "generating" | "generated" | "saving" | "saved" | "error"
  >("idle");

  // Import generate slide hook (giả sử đã có)
  // const { generateSlide, isLoading: isGenerating, response: generateResponse } = useGenerateSlide();
  const {
    saveSlide,
    isLoading: isSaving,
    response: saveResponse,
    error: saveError,
  } = useSaveSlide();

  const handleSaveSlide = async (sessionId: string) => {
    try {
      setCurrentStep("saving");
      const result = await saveSlide(sessionId);
      setCurrentStep("saved");
      return result;
    } catch (error) {
      setCurrentStep("error");
      throw error;
    }
  };

  const reset = () => {
    setCurrentStep("idle");
  };

  return {
    currentStep,
    saveSlide: handleSaveSlide,
    isSaving,
    saveResponse,
    saveError,
    reset,
  };
};

// Utility functions
export const getSavedSlideId = (response: SaveSlideResponse): number => {
  return response.id;
};

export const getSavedSessionId = (response: SaveSlideResponse): string => {
  return response.session_id;
};

export const getSavedUserId = (response: SaveSlideResponse): string => {
  return response.user_id;
};
