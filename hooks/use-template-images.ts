import { useEffect, useState, useCallback } from "react";

interface TemplateImageData {
  imageUrl: string | null;
  loading: boolean;
  error: string | null;
}

interface TemplateImagesResult {
  [templateName: string]: TemplateImageData;
}

export function useTemplateImages(templateNames: string[]) {
  const [templateImages, setTemplateImages] = useState<TemplateImagesResult>(
    {}
  );
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // Memoize templateNames để tránh re-render không cần thiết
  const templateNamesString = templateNames.join(",");

  const fetchTemplateImage = useCallback(
    async (templateName: string, signal: AbortSignal) => {
      const url = `${
        process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000"
      }/api/slide/get_template_image?template_name=${encodeURIComponent(
        templateName
      )}`;

      try {
        const res = await fetch(url, {
          method: "GET",
          signal, // Để có thể cancel request
        });

        if (!res.ok) {
          throw new Error(`HTTP ${res.status}: Không tìm thấy ảnh template`);
        }

        // Kiểm tra content type để đảm bảo là ảnh
        const contentType = res.headers.get("content-type");
        if (!contentType || !contentType.startsWith("image/")) {
          throw new Error("Response không phải là ảnh");
        }

        return {
          templateName,
          imageUrl: url,
          error: null,
        };
      } catch (err) {
        if (err instanceof Error && err.name === "AbortError") {
          throw err; // Re-throw abort errors
        }

        return {
          templateName,
          imageUrl: null,
          error: err instanceof Error ? err.message : "Lỗi không xác định",
        };
      }
    },
    []
  );

  useEffect(() => {
    if (!templateNames.length) {
      setTemplateImages({});
      setLoading(false);
      setError(null);
      return;
    }

    const abortController = new AbortController();

    setLoading(true);
    setError(null);

    // Khởi tạo state loading cho tất cả template
    const initialState: TemplateImagesResult = {};
    templateNames.forEach((name) => {
      initialState[name] = {
        imageUrl: null,
        loading: true,
        error: null,
      };
    });
    setTemplateImages(initialState);

    // Tạo promises để fetch ảnh cho từng template
    const fetchPromises = templateNames.map((templateName) =>
      fetchTemplateImage(templateName, abortController.signal)
    );

    // Xử lý tất cả promises
    Promise.allSettled(fetchPromises)
      .then((results) => {
        // Check if component was unmounted
        if (abortController.signal.aborted) return;

        const newState: TemplateImagesResult = {};
        let hasError = false;

        results.forEach((result, index) => {
          const templateName = templateNames[index];

          if (result.status === "fulfilled") {
            const data = result.value;
            newState[data.templateName] = {
              imageUrl: data.imageUrl,
              loading: false,
              error: data.error,
            };
            if (data.error) hasError = true;
          } else {
            newState[templateName] = {
              imageUrl: null,
              loading: false,
              error: "Lỗi khi tải ảnh",
            };
            hasError = true;
          }
        });

        setTemplateImages(newState);

        // Set global error nếu có lỗi
        if (hasError) {
          setError("Một số ảnh template không thể tải được");
        }
      })
      .catch((err) => {
        if (abortController.signal.aborted) return;

        console.error("Error fetching template images:", err);
        setError(err.message || "Lỗi không xác định khi tải ảnh");
      })
      .finally(() => {
        if (!abortController.signal.aborted) {
          setLoading(false);
        }
      });

    // Cleanup function
    return () => {
      abortController.abort();
    };
  }, [templateNamesString, fetchTemplateImage]);

  return { templateImages, loading, error };
}
