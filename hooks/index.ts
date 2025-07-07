// Authentication hooks
export {
  useAuth,
  useAuthToken,
  useAuthenticatedFetch,
  useRegister,
} from "./use-auth";

// API hooks
export {
  useApi,
  useCreateSlide,
  useGetSlides,
  useUpdateSlide,
  useDeleteSlide,
  useUpdateProfile,
  useChangePassword,
} from "./use-api";

// Re-export existing hooks
export { useToast } from "./use-toast";
export { useIsMobile } from "./use-mobile";
