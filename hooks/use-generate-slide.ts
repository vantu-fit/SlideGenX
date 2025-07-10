import { useState } from 'react';

// Types
interface GenerateSlideRequest {
  title: string;
  content: string;
  duration: number;
  purpose: string;
  output_file_name: string;
  template?: string;
}

interface GenerateSlideResponse {
  images_path: string[];
  session_id: string;
  output_file_name: string;
}

interface UseGenerateSlideReturn {
  generateSlide: (data: GenerateSlideRequest) => Promise<GenerateSlideResponse>;
  isLoading: boolean;
  error: string | null;
  response: GenerateSlideResponse | null;
}
const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";
// Custom hook
export const useGenerateSlide = (): UseGenerateSlideReturn => {
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [response, setResponse] = useState<GenerateSlideResponse | null>(null);

  const generateSlide = async (data: GenerateSlideRequest): Promise<GenerateSlideResponse> => {
    setIsLoading(true);
    setError(null);
    
    try {
      const response = await fetch(`${API_BASE_URL}/api/slide/generate_slide`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(data),
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || `HTTP error! status: ${response.status}`);
      }

      const result: GenerateSlideResponse = await response.json();
      setResponse(result);
      return result;
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'An unknown error occurred';
      setError(errorMessage);
      throw err;
    } finally {
      setIsLoading(false);
    }
  };

  return {
    generateSlide,
    isLoading,
    error,
    response,
  };
};

// Utility functions
export const getImagePaths = (response: GenerateSlideResponse): string[] => {
  return response.images_path;
};

export const getSessionId = (response: GenerateSlideResponse): string => {
  return response.session_id;
};

export const getOutputFileName = (response: GenerateSlideResponse): string => {
  return response.output_file_name;
};
// Example usage function
export const useSlideGenerator = () => {
  const { generateSlide, isLoading, error, response } = useGenerateSlide();

  const createSlide = async (params: {
    title: string;
    content: string;
    duration: number;
    purpose: string;
    outputFileName: string;
    template?: string;
  }) => {
    try {
      const result = await generateSlide({
        title: params.title,
        content: params.content,
        duration: params.duration,
        purpose: params.purpose,
        output_file_name: params.outputFileName,
        template: params.template,
      });

      // Extract images and session
      const imagePaths = getImagePaths(result);
      const sessionId = getSessionId(result);

      return {
        imagePaths,
        sessionId,
        fullResponse: result,
      };
    } catch (err) {
      console.error('Error generating slide:', err);
      throw err;
    }
  };

  return {
    createSlide,
    isLoading,
    error,
    response,
    imagePaths: response ? getImagePaths(response) : [],
    sessionId: response ? getSessionId(response) : null,
  };
};