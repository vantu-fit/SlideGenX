import { useEffect, useState } from "react";

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
  const [globalLoading, setGlobalLoading] = useState(false);
  const [globalError, setGlobalError] = useState<string | null>(null);

  useEffect(() => {
    if (!templateNames.length) {
      setTemplateImages({});
      setGlobalLoading(false);
      setGlobalError(null);
      return;
    }

    const abortController = new AbortController();
    setGlobalLoading(true);
    setGlobalError(null);

    const fetchAll = async () => {
      try {
        const res = await fetch(
          `${
            process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000"
          }/api/slide/get_all_template_images`,
          { method: "GET", signal: abortController.signal }
        );

        if (!res.ok) throw new Error(`HTTP ${res.status}`);

        const data: { [templateName: string]: string | null } =
          await res.json();

        const newState: TemplateImagesResult = {};
        for (const name of templateNames) {
          if (name in data) {
            newState[name] = {
              imageUrl: data[name],
              loading: false,
              error: data[name] ? null : "Không tìm thấy ảnh",
            };
          } else {
            newState[name] = {
              imageUrl: null,
              loading: false,
              error: "Không có dữ liệu",
            };
          }
        }

        setTemplateImages(newState);
        setGlobalLoading(false);
      } catch (err: any) {
        if (err.name === "AbortError") return;
        const errorMsg =
          err instanceof Error ? err.message : "Lỗi không xác định";

        const errorState: TemplateImagesResult = {};
        for (const name of templateNames) {
          errorState[name] = {
            imageUrl: null,
            loading: false,
            error: errorMsg,
          };
        }

        setTemplateImages(errorState);
        setGlobalError("Không thể tải ảnh template");
        setGlobalLoading(false);
      }
    };

    fetchAll();

    return () => abortController.abort();
  }, [templateNames]);

  return {
    templateImages,
    loading: globalLoading,
    error: globalError,
  };
}
