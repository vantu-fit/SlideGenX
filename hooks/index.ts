// Authentication hooks
export {
  useAuth,
  useAuthToken,
  useAuthenticatedFetch,
  useRegister,
} from "./use-auth";

// Slide generation hooks
export {
  useGenerateSlide,
  useSlideGenerator,
  getImagePaths,
  getSessionId,
  getOutputFileName,
} from "./use-generate-slide";

// Slide save hooks
export {
  useSaveSlide,
  useSlideWorkflow,
  getSavedSlideId,
  getSavedSessionId,
  getSavedUserId,
} from "./use-save-slide";

// Slide management hooks
export {
  useGetSlideIds,
  useGetSlideBySessionId,
  useSlideManagement,
  useSlideManagementWithAutoFetch,
  hasSlides,
  getSlideCount,
  isValidSessionId,
} from "./use-get-slides";

// Template hooks
export { useListTemplates } from "./use-list-templates";
export { useTemplateImages } from "./use-template-images";

// Utility hooks
export { useToast } from "./use-toast";
export { useIsMobile } from "./use-mobile";
