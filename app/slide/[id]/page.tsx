"use client";

import { useEffect, useState, use } from "react";
import { useRouter } from "next/navigation";
import Link from "next/link";
import { ProtectedRoute } from "@/components/protected-route";
import { useAuthContext } from "@/contexts/auth-context";
import {
  useGetSlideBySessionId,
  useGetSlideInfo,
  isValidSessionId,
  formatSlideCreatedDate,
  getSlideImageUrl,
} from "@/hooks/use-get-slides";
import { Button } from "@/components/ui/button";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Label } from "@/components/ui/label";
import { Textarea } from "@/components/ui/textarea";
import {
  AlertCircle,
  Download,
  ArrowLeft,
  FileText,
  Calendar,
  User,
  Edit3,
  Sparkles,
  Save,
  Share2,
  Trash2,
  Eye,
  RefreshCw,
} from "lucide-react";
import { Alert, AlertDescription } from "@/components/ui/alert";

interface SlidePageProps {
  params: Promise<{
    id: string;
  }>;
}

export default function SlidePage({ params }: SlidePageProps) {
  const resolvedParams = use(params);
  const { id } = resolvedParams;
  const router = useRouter();
  const { user, isAuthenticated, isLoading: isAuthLoading } = useAuthContext();
  const {
    downloadSlide,
    isLoading: isDownloading,
    error: downloadError,
  } = useGetSlideBySessionId();
  const {
    slideInfo,
    isLoading: isLoadingSlideInfo,
    error: slideInfoError,
    fetchSlideInfo,
  } = useGetSlideInfo();

  const [selectedSlideForEdit, setSelectedSlideForEdit] = useState<
    number | null
  >(null);
  const [editPrompt, setEditPrompt] = useState("");
  const [isRegenerating, setIsRegenerating] = useState(false);
  const [showDeleteConfirm, setShowDeleteConfirm] = useState(false);

  // Validate session ID format
  const isValidId = isValidSessionId(id);

  useEffect(() => {
    const loadSlideInfo = async () => {
      console.log("=== loadSlideInfo Effect ===");
      console.log("isAuthLoading:", isAuthLoading);
      console.log("isAuthenticated:", isAuthenticated);
      console.log("isValidId:", isValidId);
      console.log("user:", user);
      console.log(
        "localStorage token:",
        localStorage.getItem("access_token") ? "Present" : "Missing"
      );

      // Wait for authentication to complete
      if (isAuthLoading) {
        console.log("Still loading auth, waiting...");
        return;
      }

      // Check if user is authenticated
      if (!isAuthenticated) {
        console.log("User not authenticated, redirecting...");
        return;
      }

      // Check if ID is valid
      if (!isValidId) {
        console.log("Invalid slide ID:", id);
        return;
      }

      console.log("All checks passed, fetching slide info...");
      try {
        await fetchSlideInfo(id);
        console.log("Slide info fetch completed successfully");
      } catch (error) {
        console.error("Failed to load slide info:", error);
      }
    };

    loadSlideInfo();
  }, [id, isValidId, isAuthenticated, isAuthLoading, fetchSlideInfo, user]);

  const handleDownload = async () => {
    if (!isAuthenticated) {
      console.error("User not authenticated");
      return;
    }

    try {
      const fileName = slideInfo?.title
        ? `${slideInfo.title}_${id}.pptx`
        : `slide_${id}.pptx`;
      await downloadSlide(id, fileName);
    } catch (error) {
      console.error("Download failed:", error);
    }
  };

  const handleSlideEdit = (slideIndex: number) => {
    setSelectedSlideForEdit(slideIndex);
    setEditPrompt("");
  };

  const handleRegenerateSlide = async () => {
    if (selectedSlideForEdit === null || !editPrompt) return;

    setIsRegenerating(true);

    // Simulate API call for slide regeneration
    setTimeout(() => {
      console.log(
        `Regenerating slide ${
          selectedSlideForEdit + 1
        } with prompt: ${editPrompt}`
      );
      setSelectedSlideForEdit(null);
      setEditPrompt("");
      setIsRegenerating(false);

      // In real implementation, you would refresh the slide data here
      if (isAuthenticated) {
        fetchSlideInfo(id);
      }
    }, 2000);
  };

  const handleDeleteSlide = () => {
    console.log("Deleting slide:", id);
    setShowDeleteConfirm(false);
    // Implement delete logic here
    router.push("/dashboard");
  };

  const handleShare = () => {
    const shareUrl = `${window.location.origin}/slide/${id}`;
    navigator.clipboard.writeText(shareUrl);
    alert("Link chia sẻ đã được sao chép vào clipboard!");
  };

  // Combined loading state
  const isLoading = isAuthLoading || isLoadingSlideInfo;
  const hasError = slideInfoError || downloadError;

  // Show loading if auth is still loading
  if (isAuthLoading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto mb-4"></div>
          <p className="text-gray-600">Đang xác thực...</p>
        </div>
      </div>
    );
  }

  return (
    <ProtectedRoute>
      <div className="min-h-screen bg-gray-50">
        {/* Header */}
        <header className="bg-white border-b px-6 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-4">
              <Link href="/dashboard">
                <Button variant="ghost" size="sm">
                  <ArrowLeft className="w-4 h-4 mr-2" />
                  Quay lại Dashboard
                </Button>
              </Link>
              <div className="flex items-center space-x-3">
                <FileText className="h-6 w-6 text-blue-600" />
                <div>
                  <h1 className="text-2xl font-bold">
                    {slideInfo?.title || "Chi tiết Slide"}
                  </h1>
                  <p className="text-gray-600 text-sm">
                    {slideInfo
                      ? `${slideInfo.num_slides} slide`
                      : "Đang tải..."}
                  </p>
                </div>
              </div>
            </div>

            {slideInfo && isAuthenticated && (
              <div className="flex items-center space-x-2">
                <Button variant="outline" size="sm" onClick={handleShare}>
                  <Share2 className="w-4 h-4 mr-2" />
                  Chia sẻ
                </Button>

                <Button
                  variant="outline"
                  size="sm"
                  onClick={() => setShowDeleteConfirm(true)}
                  className="text-red-600 hover:text-red-700"
                >
                  <Trash2 className="w-4 h-4 mr-2" />
                  Xóa
                </Button>

                <Button
                  onClick={handleDownload}
                  disabled={isDownloading}
                  className="bg-gradient-to-r from-green-800 to-green-700 hover:from-green-900 hover:to-green-800 text-white"
                >
                  {isDownloading ? (
                    <>
                      <RefreshCw className="w-4 h-4 mr-2 animate-spin" />
                      Đang tải xuống...
                    </>
                  ) : (
                    <>
                      <Download className="w-4 h-4 mr-2" />
                      Tải xuống .pptx
                    </>
                  )}
                </Button>
              </div>
            )}
          </div>
        </header>

        <div className="container mx-auto px-6 py-8">
          {/* Error Display */}
          {hasError && (
            <Alert className="mb-6 border-red-200 bg-red-50">
              <AlertCircle className="h-4 w-4 text-red-600" />
              <AlertDescription className="text-red-800">
                {slideInfoError && `Lỗi tải slide: ${slideInfoError}`}
                {downloadError && `Lỗi tải xuống slide: ${downloadError}`}
              </AlertDescription>
            </Alert>
          )}

          {/* Loading State */}
          {isLoading && (
            <div className="text-center py-12">
              <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto mb-4"></div>
              <p className="text-gray-600">Đang tải chi tiết slide...</p>
            </div>
          )}

          {/* Invalid ID */}
          {!isLoading && !isValidId && (
            <div className="text-center py-12">
              <Alert className="max-w-md mx-auto border-red-200 bg-red-50">
                <AlertCircle className="h-4 w-4 text-red-600" />
                <AlertDescription className="text-red-800">
                  ID slide không hợp lệ. Vui lòng kiểm tra URL và thử lại.
                </AlertDescription>
              </Alert>
            </div>
          )}

          {/* Slide Not Found */}
          {!isLoading &&
            isValidId &&
            !slideInfo &&
            !hasError &&
            isAuthenticated && (
              <div className="text-center py-12">
                <AlertCircle className="h-16 w-16 text-red-500 mx-auto mb-4" />
                <h2 className="text-2xl font-semibold text-gray-900 mb-2">
                  Không tìm thấy Slide
                </h2>
                <p className="text-gray-600 mb-6">
                  Slide bạn đang tìm không tồn tại hoặc bạn không có quyền xem.
                </p>
                <Link href="/dashboard">
                  <Button variant="outline">Quay lại Dashboard</Button>
                </Link>
              </div>
            )}

          {/* Slide Details */}
          {!isLoading && isValidId && slideInfo && isAuthenticated && (
            <div className="max-w-7xl mx-auto">
              {/* Slide Information */}
              <div className="grid lg:grid-cols-3 gap-8 mb-8">
                <Card className="lg:col-span-2">
                  <CardHeader>
                    <div className="flex items-center justify-between">
                      <div>
                        <CardTitle className="text-xl">
                          Thông tin Slide
                        </CardTitle>
                        <CardDescription>
                          Chi tiết về bài thuyết trình của bạn
                        </CardDescription>
                      </div>
                      <Badge variant="default" className="text-sm">
                        Hoạt động
                      </Badge>
                    </div>
                  </CardHeader>
                  <CardContent className="space-y-4">
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                      <div className="flex items-center space-x-3">
                        <FileText className="h-5 w-5 text-gray-500" />
                        <div>
                          <p className="text-sm font-medium text-gray-900">
                            Session ID
                          </p>
                          <p className="text-xs text-gray-600 font-mono break-all">
                            {slideInfo.session_id}
                          </p>
                        </div>
                      </div>

                      <div className="flex items-center space-x-3">
                        <User className="h-5 w-5 text-gray-500" />
                        <div>
                          <p className="text-sm font-medium text-gray-900">
                            Tạo bởi
                          </p>
                          <p className="text-sm text-gray-600">
                            {user?.full_name || user?.username || "Không rõ"}
                          </p>
                        </div>
                      </div>

                      <div className="flex items-center space-x-3">
                        <Calendar className="h-5 w-5 text-gray-500" />
                        <div>
                          <p className="text-sm font-medium text-gray-900">
                            Ngày tạo
                          </p>
                          <p className="text-sm text-gray-600">
                            {formatSlideCreatedDate(slideInfo.created_at)}
                          </p>
                        </div>
                      </div>

                      <div className="flex items-center space-x-3">
                        <FileText className="h-5 w-5 text-gray-500" />
                        <div>
                          <p className="text-sm font-medium text-gray-900">
                            Template
                          </p>
                          <p className="text-sm text-gray-600">
                            {slideInfo.template || "Template Mặc định"}
                          </p>
                        </div>
                      </div>
                    </div>
                  </CardContent>
                </Card>

                <Card>
                  <CardHeader>
                    <CardTitle className="text-xl">Thao tác nhanh</CardTitle>
                    <CardDescription>
                      Quản lý bài thuyết trình của bạn
                    </CardDescription>
                  </CardHeader>
                  <CardContent className="space-y-3">
                    <Button
                      variant="outline"
                      className="w-full justify-start"
                      onClick={handleShare}
                    >
                      <Share2 className="w-4 h-4 mr-2" />
                      Chia sẻ Bài thuyết trình
                    </Button>
                    <Button variant="outline" className="w-full justify-start">
                      <Eye className="w-4 h-4 mr-2" />
                      Chế độ xem trước
                    </Button>
                    <Button variant="outline" className="w-full justify-start">
                      <RefreshCw className="w-4 h-4 mr-2" />
                      Tạo lại tất cả
                    </Button>
                  </CardContent>
                </Card>
              </div>

              {/* Slides Preview */}
              <div className="mb-6">
                <h2 className="text-2xl font-semibold mb-4">Xem trước Slide</h2>
                <p className="text-gray-600 mb-6">
                  Nhấp vào bất kỳ slide nào để chỉnh sửa hoặc tạo lại
                </p>
              </div>

              <div className="flex flex-col gap-8 items-center">
                {slideInfo.slide_details.map((slide, index) => (
                  <Card
                    key={slide.slide_index}
                    className="cursor-pointer hover:shadow-lg transition-all duration-200 w-full max-w-5xl hover:scale-[1.02]"
                    onClick={() => handleSlideEdit(index)}
                  >
                    <CardContent className="p-0">
                      <div className="relative">
                        <img
                          src={getSlideImageUrl(slideInfo.session_id, index)}
                          alt={slide.title}
                          className="w-full h-[600px] object-cover rounded"
                          onError={(e) => {
                            (e.target as HTMLImageElement).src =
                              "/placeholder.svg";
                          }}
                        />
                        <Badge className="absolute top-4 left-4 bg-blue-600">
                          Slide {index + 1}
                        </Badge>
                        <Button
                          size="sm"
                          className="absolute top-4 right-4 bg-gradient-to-r from-green-800 to-green-700 hover:from-green-900 hover:to-green-800 text-white"
                        >
                          <Edit3 className="w-3 h-3 mr-1" />
                          Chỉnh sửa
                        </Button>

                        {/* Slide Info Overlay */}
                        <div className="absolute bottom-0 left-0 right-0 bg-gradient-to-t from-black/70 to-transparent p-6 text-white rounded-b">
                          <h3 className="text-lg font-semibold mb-2">
                            {slide.title}
                          </h3>
                          <p className="text-sm opacity-90">
                            {Array.isArray(slide.content)
                              ? slide.content.join(" ")
                              : slide.content || "Không có nội dung"}
                          </p>
                          <div className="flex items-center gap-2 mt-2">
                            {slide.has_images && (
                              <Badge variant="secondary" className="text-xs">
                                Hình ảnh
                              </Badge>
                            )}
                            {slide.has_diagrams && (
                              <Badge variant="secondary" className="text-xs">
                                Biểu đồ
                              </Badge>
                            )}
                            {slide.keywords.length > 0 && (
                              <Badge variant="secondary" className="text-xs">
                                {slide.keywords.length} Từ khóa
                              </Badge>
                            )}
                          </div>
                        </div>
                      </div>
                    </CardContent>
                  </Card>
                ))}
              </div>

              {/* Edit Slide Modal */}
              {selectedSlideForEdit !== null && (
                <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50">
                  <Card className="w-full max-w-md">
                    <CardHeader>
                      <CardTitle>
                        Chỉnh sửa Slide {selectedSlideForEdit + 1}
                      </CardTitle>
                      <CardDescription>
                        Mô tả cách bạn muốn chỉnh sửa slide này
                      </CardDescription>
                    </CardHeader>
                    <CardContent className="space-y-4">
                      <div>
                        <Label htmlFor="edit-prompt">Hướng dẫn chỉnh sửa</Label>
                        <Textarea
                          id="edit-prompt"
                          placeholder="Ví dụ: Làm cho trực quan hơn, thêm thống kê, thay đổi tông điệu, bao gồm thêm chi tiết về..."
                          value={editPrompt}
                          onChange={(e) => setEditPrompt(e.target.value)}
                          rows={4}
                        />
                      </div>
                      <div className="flex justify-end space-x-2">
                        <Button
                          variant="outline"
                          onClick={() => setSelectedSlideForEdit(null)}
                          disabled={isRegenerating}
                        >
                          Hủy
                        </Button>
                        <Button
                          onClick={handleRegenerateSlide}
                          disabled={!editPrompt.trim() || isRegenerating}
                          className="bg-gradient-to-r from-green-800 to-green-700 hover:from-green-900 hover:to-green-800 text-white"
                        >
                          {isRegenerating ? (
                            <>
                              <RefreshCw className="w-4 h-4 mr-2 animate-spin" />
                              Đang tạo lại...
                            </>
                          ) : (
                            <>
                              <Sparkles className="w-4 h-4 mr-2" />
                              Tạo lại Slide
                            </>
                          )}
                        </Button>
                      </div>
                    </CardContent>
                  </Card>
                </div>
              )}

              {/* Delete Confirmation Modal */}
              {showDeleteConfirm && (
                <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50">
                  <Card className="w-full max-w-md">
                    <CardHeader>
                      <CardTitle className="text-red-600">
                        Xóa Bài thuyết trình
                      </CardTitle>
                      <CardDescription>
                        Bạn có chắc chắn muốn xóa bài thuyết trình này? Hành động này
                        không thể hoàn tác.
                      </CardDescription>
                    </CardHeader>
                    <CardContent>
                      <div className="flex justify-end space-x-2">
                        <Button
                          variant="outline"
                          onClick={() => setShowDeleteConfirm(false)}
                        >
                          Hủy
                        </Button>
                        <Button
                          onClick={handleDeleteSlide}
                          className="bg-red-600 hover:bg-red-700 text-white"
                        >
                          <Trash2 className="w-4 h-4 mr-2" />
                          Xóa
                        </Button>
                      </div>
                    </CardContent>
                  </Card>
                </div>
              )}
            </div>
          )}
        </div>
      </div>
    </ProtectedRoute>
  );
}
