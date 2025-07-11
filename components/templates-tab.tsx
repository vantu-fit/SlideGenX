"use client";

import { useState, useMemo } from "react";
import { Button } from "@/components/ui/button";
import { Card, CardContent } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Badge } from "@/components/ui/badge";
import { Search, Star } from "lucide-react";
import { useListTemplates } from "@/hooks/use-list-templates";
import { useTemplateImages } from "@/hooks/use-template-images";

const categories = [
  "Tất cả",
  "Kinh doanh",
  "Giáo dục",
  "Tiếp thị",
  "Sáng tạo",
  "Tài chính",
];

// Hàm tạo mock data cho template
const generateMockData = (templateName: string, index: number) => {
  // Tạo category dựa trên tên template
  let category = "Kinh doanh";
  const name = templateName.toLowerCase();
  if (
    name.includes("academic") ||
    name.includes("education") ||
    name.includes("training")
  ) {
    category = "Giáo dục";
  } else if (name.includes("marketing") || name.includes("pitch")) {
    category = "Tiếp thị";
  } else if (
    name.includes("creative") ||
    name.includes("portfolio") ||
    name.includes("design")
  ) {
    category = "Sáng tạo";
  } else if (
    name.includes("financial") ||
    name.includes("finance") ||
    name.includes("budget")
  ) {
    category = "Tài chính";
  }

  // Tạo các giá trị mock khác
  const isPremium = Math.random() > 0.6; // 40% chance premium
  const rating = Number((4.2 + Math.random() * 0.8).toFixed(1)); // 4.2-5.0
  const downloads = Math.floor(500 + Math.random() * 3000); // 500-3500

  return {
    category,
    isPremium,
    rating,
    downloads,
  };
};

export function TemplatesTab() {
  const [searchTerm, setSearchTerm] = useState("");
  const [selectedCategory, setSelectedCategory] = useState("Tất cả");

  // Sử dụng hooks để lấy templates và images
  const {
    templates,
    loading: loadingTemplates,
    error: errorTemplates,
  } = useListTemplates();

  const {
    templateImages,
    loading: loadingImages,
    error: errorImages,
  } = useTemplateImages(templates);

  // Tạo templates với mock data
  const templatesWithMockData = useMemo(() => {
    return templates.map((templateName, index) => ({
      id: index + 1,
      title: templateName,
      thumbnail: templateImages[templateName]?.imageUrl || "/placeholder.svg",
      loading: loadingImages || templateImages[templateName]?.loading,
      error: templateImages[templateName]?.error,
      ...generateMockData(templateName, index),
    }));
  }, [templates, templateImages, loadingImages]);

  const filteredTemplates = templatesWithMockData.filter((template) => {
    const matchesSearch = template.title
      .toLowerCase()
      .includes(searchTerm.toLowerCase());
    const matchesCategory =
      selectedCategory === "Tất cả" || template.category === selectedCategory;
    return matchesSearch && matchesCategory;
  });

  const handleSelectTemplate = (templateId: number) => {
    // In a real app, this would navigate to create page with selected template
    console.log("Selected template:", templateId);
  };

  if (loadingTemplates) {
    return (
      <div className="space-y-6">
        <div className="space-y-4">
          <div className="h-10 bg-gray-200 rounded animate-pulse max-w-md" />
          <div className="flex flex-wrap gap-2">
            {categories.map((category) => (
              <div
                key={category}
                className="h-8 w-20 bg-gray-200 rounded animate-pulse"
              />
            ))}
          </div>
        </div>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6">
          {[...Array(8)].map((_, i) => (
            <div
              key={i}
              className="h-64 bg-gray-200 rounded-lg animate-pulse"
            />
          ))}
        </div>
      </div>
    );
  }

  if (errorTemplates) {
    return (
      <div className="text-center py-12">
        <p className="text-red-600">
          Không thể tải danh sách template: {errorTemplates}
        </p>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Search and Categories */}
      <div className="space-y-4">
        <div className="relative max-w-md">
          <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 w-4 h-4" />
          <Input
            placeholder="Tìm kiếm template..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            className="pl-10"
          />
        </div>

        <div className="flex flex-wrap gap-2">
          {categories.map((category) => (
            <Button
              key={category}
              variant={selectedCategory === category ? "default" : "outline"}
              size="sm"
              onClick={() => setSelectedCategory(category)}
            >
              {category}
            </Button>
          ))}
        </div>
      </div>

      {/* Templates Grid */}
      {filteredTemplates.length > 0 ? (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6">
          {filteredTemplates.map((template) => (
            <Card
              key={template.id}
              className="group hover:shadow-lg transition-shadow cursor-pointer"
              onClick={() => handleSelectTemplate(template.id)}
            >
              <CardContent className="p-0">
                <div className="relative">
                  {template.loading ? (
                    <div className="w-full h-40 bg-gray-200 rounded-t-lg animate-pulse" />
                  ) : (
                    <img
                      src={"http://localhost:8000/image/" + template.thumbnail}
                      alt={template.title}
                      className="w-full h-40 object-cover rounded-t-lg"
                      onError={(e) => {
                        (e.target as HTMLImageElement).src = "/placeholder.svg";
                      }}
                    />
                  )}
                  {template.isPremium && (
                    <Badge className="absolute top-2 right-2 bg-gradient-to-r from-yellow-400 to-orange-500">
                      Premium
                    </Badge>
                  )}
                  <div className="absolute inset-0 bg-black bg-opacity-0 group-hover:bg-opacity-20 transition-all rounded-t-lg flex items-center justify-center">
                    <Button
                      className="opacity-0 group-hover:opacity-100 transition-opacity"
                      size="sm"
                    >
                      Sử dụng Template
                    </Button>
                  </div>
                </div>
                <div className="p-4">
                  <div className="flex items-start justify-between mb-2">
                    <h3 className="font-semibold line-clamp-1 flex-1">
                      {template.title}
                    </h3>
                  </div>
                  <div className="flex items-center justify-between text-sm text-gray-600">
                    <Badge variant="secondary" className="text-xs">
                      {template.category}
                    </Badge>
                    <div className="flex items-center space-x-1">
                      <Star className="w-3 h-3 fill-yellow-400 text-yellow-400" />
                      <span>{template.rating}</span>
                    </div>
                  </div>
                  <p className="text-xs text-gray-500 mt-1">
                    {template.downloads.toLocaleString()} lượt tải
                  </p>
                  {template.error && (
                    <p className="text-xs text-red-400 mt-1">
                      Lỗi tải ảnh: {template.error}
                    </p>
                  )}
                </div>
              </CardContent>
            </Card>
          ))}
        </div>
      ) : (
        <div className="text-center py-12">
          <p className="text-gray-600">
            Không tìm thấy template nào phù hợp với tiêu chí của bạn.
          </p>
        </div>
      )}

      {errorImages && (
        <div className="text-orange-500 text-sm mt-4">
          Một số ảnh template không thể tải: {errorImages}
        </div>
      )}
    </div>
  );
}
