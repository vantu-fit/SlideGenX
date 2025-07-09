"use client";

import type React from "react";

import { useState } from "react";
import Link from "next/link";
import { Button } from "@/components/ui/button";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { Label } from "@/components/ui/label";
import { Textarea } from "@/components/ui/textarea";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Badge } from "@/components/ui/badge";
import {
  ArrowLeft,
  Upload,
  FileText,
  Sparkles,
  Download,
  Save,
  Edit3,
  ChevronLeft,
  ChevronRight,
} from "lucide-react";
import { useListTemplates } from "@/hooks/use-list-templates";
import { useTemplateImages } from "@/hooks/use-template-images";

// Mock slide data
const mockSlides = [
  {
    id: 1,
    title: "Introduction",
    content:
      "Welcome to our presentation about sustainable energy solutions for the future.",
    thumbnail: "/placeholder.svg?height=200&width=300",
  },
  {
    id: 2,
    title: "Current Challenges",
    content:
      "The world faces significant energy challenges including climate change and resource depletion.",
    thumbnail: "/placeholder.svg?height=200&width=300",
  },
  {
    id: 3,
    title: "Solar Energy Solutions",
    content:
      "Solar power offers clean, renewable energy with decreasing costs and increasing efficiency.",
    thumbnail: "/placeholder.svg?height=200&width=300",
  },
  {
    id: 4,
    title: "Implementation Strategy",
    content:
      "A phased approach to implementing renewable energy solutions across different sectors.",
    thumbnail: "/placeholder.svg?height=200&width=300",
  },
  {
    id: 5,
    title: "Conclusion",
    content:
      "Together, we can build a sustainable energy future for generations to come.",
    thumbnail: "/placeholder.svg?height=200&width=300",
  },
];

export default function CreateSlidePage() {
  const [selectedTemplate, setSelectedTemplate] = useState<number | null>(null);
  const [topic, setTopic] = useState("");
  const [contentFile, setContentFile] = useState<File | null>(null);
  const [isGenerating, setIsGenerating] = useState(false);
  const [generatedSlides, setGeneratedSlides] = useState<typeof mockSlides>([]);
  const [selectedSlide, setSelectedSlide] = useState<number | null>(null);
  const [editPrompt, setEditPrompt] = useState("");
  const [currentPage, setCurrentPage] = useState(0);

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

  // Phân trang templates
  const templatesPerPage = 4;
  const totalPages = Math.ceil(templates.length / templatesPerPage);
  const currentTemplates = templates.slice(
    currentPage * templatesPerPage,
    (currentPage + 1) * templatesPerPage
  );

  const handlePreviousPage = () => {
    setCurrentPage((prev) => Math.max(0, prev - 1));
  };

  const handleNextPage = () => {
    setCurrentPage((prev) => Math.min(totalPages - 1, prev + 1));
  };

  const handleTemplateSelect = (localIndex: number) => {
    const globalIndex = currentPage * templatesPerPage + localIndex;
    setSelectedTemplate(globalIndex);
  };

  const isTemplateSelected = (localIndex: number) => {
    const globalIndex = currentPage * templatesPerPage + localIndex;
    return selectedTemplate === globalIndex;
  };

  const handleFileUpload = (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (file) {
      setContentFile(file);
    }
  };

  const handleGenerate = async () => {
    if (!selectedTemplate || (!topic && !contentFile)) return;

    setIsGenerating(true);

    // Simulate AI generation
    setTimeout(() => {
      setGeneratedSlides(mockSlides);
      setIsGenerating(false);
    }, 3000);
  };

  const handleSlideEdit = (slideId: number) => {
    setSelectedSlide(slideId);
  };

  const handleRegenerateSlide = () => {
    if (!selectedSlide || !editPrompt) return;

    // Simulate slide regeneration
    setTimeout(() => {
      setSelectedSlide(null);
      setEditPrompt("");
    }, 1500);
  };

  const handleSave = () => {
    // Simulate saving to slides
    alert("Slides saved successfully!");
  };

  const handleDownload = () => {
    // Simulate download
    alert("Downloading presentation as .pptx...");
  };

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-white border-b px-6 py-4">
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-4">
            <Link href="/dashboard">
              <Button variant="ghost" size="sm">
                <ArrowLeft className="w-4 h-4 mr-2" />
                Back to Dashboard
              </Button>
            </Link>
            <h1 className="text-2xl font-bold">Create New Slide</h1>
          </div>
          {generatedSlides.length > 0 && (
            <div className="flex items-center space-x-2">
              <Button onClick={handleSave} variant="outline">
                <Save className="w-4 h-4 mr-2" />
                Save
              </Button>
              <Button
                onClick={handleDownload}
                className="bg-gradient-to-r from-green-800 to-green-700 hover:from-green-900 hover:to-green-800 text-white"
              >
                <Download className="w-4 h-4 mr-2" />
                Download .pptx
              </Button>
            </div>
          )}
        </div>
      </header>

      <div className="container mx-auto px-6 py-8">
        {generatedSlides.length === 0 ? (
          <div className="max-w-4xl mx-auto">
            <div className="grid lg:grid-cols-2 gap-8">
              {/* Template Selection */}
              <Card>
                <CardHeader>
                  <CardTitle>1. Choose Template</CardTitle>
                  <CardDescription>
                    Select a template or upload your own .pptx file
                  </CardDescription>
                </CardHeader>
                <CardContent>
                  <Tabs defaultValue="templates">
                    <TabsList className="grid w-full grid-cols-2">
                      <TabsTrigger value="templates">Templates</TabsTrigger>
                      <TabsTrigger value="upload">Upload</TabsTrigger>
                    </TabsList>
                    <TabsContent value="templates" className="space-y-4">
                      {loadingTemplates ? (
                        <div className="grid grid-cols-2 gap-4">
                          {[...Array(4)].map((_, i) => (
                            <div
                              key={i}
                              className="animate-pulse h-36 bg-gray-200 rounded-lg"
                            />
                          ))}
                        </div>
                      ) : errorTemplates ? (
                        <div className="text-red-500">
                          Không thể tải danh sách template: {errorTemplates}
                        </div>
                      ) : (
                        <>
                          <div className="grid grid-cols-2 gap-4">
                            {currentTemplates.map((templateName, localIdx) => {
                              const imageData = templateImages[templateName];
                              const isLoading =
                                loadingImages || imageData?.loading;
                              const imageUrl = imageData?.imageUrl;
                              const imageError = imageData?.error;

                              return (
                                <div
                                  key={templateName}
                                  className={`cursor-pointer rounded-lg border-2 p-3 transition-colors ${
                                    isTemplateSelected(localIdx)
                                      ? "border-blue-500 bg-blue-50"
                                      : "border-gray-200 hover:border-gray-300"
                                  }`}
                                  onClick={() => handleTemplateSelect(localIdx)}
                                >
                                  {isLoading ? (
                                    <div className="animate-pulse h-24 bg-gray-200 rounded mb-2" />
                                  ) : (
                                    <img
                                      src={imageUrl || "/placeholder.svg"}
                                      alt={templateName}
                                      className="w-full h-24 object-cover rounded mb-2"
                                      onError={(e) => {
                                        (e.target as HTMLImageElement).src =
                                          "/placeholder.svg";
                                      }}
                                    />
                                  )}
                                  <p className="text-sm font-medium text-center">
                                    {templateName}
                                  </p>
                                  {imageError && (
                                    <p className="text-xs text-red-400 text-center mt-1">
                                      {imageError}
                                    </p>
                                  )}
                                </div>
                              );
                            })}
                          </div>

                          {/* Pagination Controls */}
                          {totalPages > 1 && (
                            <div className="flex items-center justify-between mt-4">
                              <Button
                                variant="outline"
                                size="sm"
                                onClick={handlePreviousPage}
                                disabled={currentPage === 0}
                              >
                                <ChevronLeft className="w-4 h-4 mr-1" />
                                Previous
                              </Button>

                              <div className="flex items-center space-x-2">
                                <span className="text-sm text-gray-600">
                                  Page {currentPage + 1} of {totalPages}
                                </span>
                                <div className="flex space-x-1">
                                  {Array.from({ length: totalPages }).map(
                                    (_, idx) => (
                                      <button
                                        key={idx}
                                        onClick={() => setCurrentPage(idx)}
                                        className={`w-2 h-2 rounded-full ${
                                          idx === currentPage
                                            ? "bg-blue-500"
                                            : "bg-gray-300"
                                        }`}
                                      />
                                    )
                                  )}
                                </div>
                              </div>

                              <Button
                                variant="outline"
                                size="sm"
                                onClick={handleNextPage}
                                disabled={currentPage === totalPages - 1}
                              >
                                Next
                                <ChevronRight className="w-4 h-4 ml-1" />
                              </Button>
                            </div>
                          )}
                        </>
                      )}
                      {errorImages && (
                        <div className="text-orange-500 text-sm mt-2">
                          Một số ảnh template không thể tải: {errorImages}
                        </div>
                      )}
                    </TabsContent>
                    <TabsContent value="upload">
                      <div className="border-2 border-dashed border-gray-300 rounded-lg p-8 text-center">
                        <Upload className="w-12 h-12 text-gray-400 mx-auto mb-4" />
                        <p className="text-gray-600 mb-4">
                          Upload your .pptx template
                        </p>
                        <Button variant="outline">
                          <Upload className="w-4 h-4 mr-2" />
                          Choose File
                        </Button>
                      </div>
                    </TabsContent>
                  </Tabs>
                </CardContent>
              </Card>

              {/* Content Input */}
              <Card>
                <CardHeader>
                  <CardTitle>2. Add Content</CardTitle>
                  <CardDescription>
                    Provide your topic or upload content file
                  </CardDescription>
                </CardHeader>
                <CardContent>
                  <Tabs defaultValue="topic">
                    <TabsList className="grid w-full grid-cols-2">
                      <TabsTrigger value="topic">Topic</TabsTrigger>
                      <TabsTrigger value="file">File Upload</TabsTrigger>
                    </TabsList>
                    <TabsContent value="topic" className="space-y-4">
                      <div>
                        <Label htmlFor="topic">Presentation Topic</Label>
                        <Textarea
                          id="topic"
                          placeholder="Enter your presentation topic or key points..."
                          value={topic}
                          onChange={(e) => setTopic(e.target.value)}
                          rows={6}
                        />
                      </div>
                    </TabsContent>
                    <TabsContent value="file">
                      <div className="border-2 border-dashed border-gray-300 rounded-lg p-8 text-center">
                        <FileText className="w-12 h-12 text-gray-400 mx-auto mb-4" />
                        <p className="text-gray-600 mb-4">
                          Upload .txt file with your content
                        </p>
                        <input
                          type="file"
                          accept=".txt"
                          onChange={handleFileUpload}
                          className="hidden"
                          id="content-file"
                        />
                        <label htmlFor="content-file">
                          <Button variant="outline" asChild>
                            <span>
                              <Upload className="w-4 h-4 mr-2" />
                              Choose File
                            </span>
                          </Button>
                        </label>
                        {contentFile && (
                          <p className="text-sm text-green-600 mt-2">
                            File uploaded: {contentFile.name}
                          </p>
                        )}
                      </div>
                    </TabsContent>
                  </Tabs>
                </CardContent>
              </Card>
            </div>

            {/* Generate Button */}
            <div className="text-center mt-8">
              <Button
                onClick={handleGenerate}
                disabled={
                  !selectedTemplate || (!topic && !contentFile) || isGenerating
                }
                size="lg"
                className="bg-gradient-to-r from-green-800 to-green-700 hover:from-green-900 hover:to-green-800 text-white"
              >
                {isGenerating ? (
                  <>
                    <Sparkles className="w-5 h-5 mr-2 animate-spin" />
                    Generating Slides...
                  </>
                ) : (
                  <>
                    <Sparkles className="w-5 h-5 mr-2" />
                    Generate Slides with AI
                  </>
                )}
              </Button>
            </div>
          </div>
        ) : (
          /* Generated Slides Preview */
          <div className="max-w-7xl mx-auto">
            <div className="flex flex-col gap-12 items-center">
              {generatedSlides.map((slide, index) => (
                <Card
                  key={slide.id}
                  className="cursor-pointer hover:shadow-lg transition-shadow w-full max-w-5xl"
                  onClick={() => handleSlideEdit(slide.id)}
                >
                  <CardContent className="p-0">
                    <div className="relative">
                      <img
                        src={slide.thumbnail || "/placeholder.svg"}
                        alt={slide.title}
                        className="w-full h-[600px] object-cover rounded"
                      />
                      <Badge className="absolute top-2 left-2">
                        {index + 1}
                      </Badge>
                      <Button
                        size="sm"
                        variant="secondary"
                        className="absolute top-2 right-2 bg-gradient-to-r from-green-800 to-green-700 hover:from-green-900 hover:to-green-800 text-white"
                      >
                        <Edit3 className="w-3 h-3" />
                      </Button>
                    </div>
                  </CardContent>
                </Card>
              ))}
            </div>

            {/* Edit Slide Modal */}
            {selectedSlide && (
              <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50">
                <Card className="w-full max-w-md">
                  <CardHeader>
                    <CardTitle>Edit Slide</CardTitle>
                    <CardDescription>
                      Describe how you want to modify this slide
                    </CardDescription>
                  </CardHeader>
                  <CardContent className="space-y-4">
                    <Textarea
                      placeholder="e.g., Make it more visual, add statistics, change the tone..."
                      value={editPrompt}
                      onChange={(e) => setEditPrompt(e.target.value)}
                      rows={4}
                    />
                    <div className="flex justify-end space-x-2">
                      <Button
                        variant="outline"
                        onClick={() => setSelectedSlide(null)}
                      >
                        Cancel
                      </Button>
                      <Button
                        onClick={handleRegenerateSlide}
                        className="bg-gradient-to-r from-green-800 to-green-700 hover:from-green-900 hover:to-green-800 text-white"
                      >
                        <Sparkles className="w-4 h-4 mr-2" />
                        Regenerate
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
  );
}
