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
  AlertCircle,
} from "lucide-react";
import { useListTemplates } from "@/hooks/use-list-templates";
import { useTemplateImages } from "@/hooks/use-template-images";
import { useGenerateSlide, useSaveSlide } from "@/hooks";
import { Alert, AlertDescription } from "@/components/ui/alert";

// Interface for slide data
interface SlideData {
  id: string;
  title: string;
  content: string;
  thumbnail: string;
  imagePath: string;
}

export default function CreateSlidePage() {
  const [selectedTemplate, setSelectedTemplate] = useState<number | null>(null);
  const [topic, setTopic] = useState("");
  const [contentFile, setContentFile] = useState<File | null>(null);
  const [generatedSlides, setGeneratedSlides] = useState<SlideData[]>([]);
  const [selectedSlide, setSelectedSlide] = useState<number | null>(null);
  const [editPrompt, setEditPrompt] = useState("");
  const [currentPage, setCurrentPage] = useState(0);
  const [sessionId, setSessionId] = useState<string | null>(null);

  // Form fields for slide generation
  const [slideTitle, setSlideTitle] = useState("");
  const [duration, setDuration] = useState(60);
  const [purpose, setPurpose] = useState("");
  const [outputFileName, setOutputFileName] = useState("");

  // Sử dụng hooks
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

  const {
    generateSlide,
    isLoading: isGenerating,
    error: generateError,
    response: generateResponse,
  } = useGenerateSlide();

  const {
    saveSlide,
    isLoading: isSaving,
    error: saveError,
    response: saveResponse,
    reset: resetSave,
  } = useSaveSlide();

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
      // Auto-generate output filename from uploaded file
      const fileName = file.name.split(".")[0];
      setOutputFileName(fileName);
    }
  };

  const handleTemplateUpload = (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (file) {
      console.log("Template file uploaded:", file.name);
    }
  };

  const handleGenerate = async () => {
    if (selectedTemplate === null || (!topic && !contentFile)) return;

    try {
      // Reset save state for new generation
      resetSave();

      // Prepare content
      let content = topic;
      if (contentFile) {
        // If file is uploaded, read its content
        const fileContent = await readFileContent(contentFile);
        content = fileContent;
      }

      // Get selected template name
      const selectedTemplateName = templates[selectedTemplate] || "";

      // Generate unique output filename if not provided
      const finalOutputFileName = outputFileName || `slide_${Date.now()}`;
      // Call API to generate slides
      const result = await generateSlide({
        title: slideTitle || "Generated Presentation",
        content: content,
        duration: duration,
        purpose: purpose || "presentation",
        output_file_name: finalOutputFileName,
        template: selectedTemplateName,
      });

      // Convert API response to slide data
      const slides: SlideData[] = result.images_path.map(
        (imagePath, index) => ({
          id: `slide_${index + 1}`,
          title: `Slide ${index + 1}`,
          content: `Generated slide content ${index + 1}`,
          thumbnail: `http://localhost:8000/image/${imagePath}`,
          imagePath: imagePath,
        })
      );

      setGeneratedSlides(slides);
      setSessionId(result.session_id);
      setOutputFileName(result.output_file_name);
    } catch (error) {
      console.error("Error generating slides:", error);
    }
  };

  const readFileContent = (file: File): Promise<string> => {
    return new Promise((resolve, reject) => {
      const reader = new FileReader();
      reader.onload = (e) => {
        const content = e.target?.result as string;
        resolve(content);
      };
      reader.onerror = reject;
      reader.readAsText(file);
    });
  };

  const handleSlideEdit = (slideId: string) => {
    const slideIndex = generatedSlides.findIndex(
      (slide) => slide.id === slideId
    );
    setSelectedSlide(slideIndex);
  };

  const handleRegenerateSlide = () => {
    if (selectedSlide === null || !editPrompt) return;

    // Simulate slide regeneration
    setTimeout(() => {
      setSelectedSlide(null);
      setEditPrompt("");
    }, 1500);
  };

  const handleSave = async () => {
    if (!sessionId) {
      alert("No session to save!");
      return;
    }

    try {
      await saveSlide(sessionId);
      // Success notification will be handled by the UI update
    } catch (error) {
      console.error("Error saving slide:", error);
    }
  };

  const handleDownload = async () => {
    if (sessionId && outputFileName) {
      const downloadUrl = `http://localhost:8000/${sessionId}/${outputFileName}`;

      const response = await fetch(downloadUrl);
      const blob = await response.blob();
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement("a");
      a.href = url;
      a.download = outputFileName;
      a.click();
    }
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
              <Button
                variant="ghost"
                onClick={() => {
                  setGeneratedSlides([]);
                  setSessionId(null);
                  setTopic("");
                  setContentFile(null);
                  setSlideTitle("");
                  setDuration(60);
                  setPurpose("");
                  setOutputFileName("");
                  resetSave();
                }}
              >
                <ArrowLeft className="w-4 h-4 mr-2" />
                Create New
              </Button>

              {!saveResponse ? (
                <Button
                  onClick={handleSave}
                  variant="outline"
                  disabled={isSaving}
                >
                  {isSaving ? (
                    <>
                      <Sparkles className="w-4 h-4 mr-2 animate-spin" />
                      Saving...
                    </>
                  ) : (
                    <>
                      <Save className="w-4 h-4 mr-2" />
                      Save
                    </>
                  )}
                </Button>
              ) : (
                <Button variant="outline" disabled className="text-green-600">
                  <Save className="w-4 h-4 mr-2" />
                  Saved ✓
                </Button>
              )}

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
        {/* Error Display */}
        {(generateError || saveError) && (
          <Alert className="mb-6 border-red-200 bg-red-50">
            <AlertCircle className="h-4 w-4 text-red-600" />
            <AlertDescription className="text-red-800">
              {generateError && `Error generating slides: ${generateError}`}
              {saveError && `Error saving slides: ${saveError}`}
            </AlertDescription>
          </Alert>
        )}

        {/* Success Display */}
        {saveResponse && (
          <Alert className="mb-6 border-green-200 bg-green-50">
            <Save className="h-4 w-4 text-green-600" />
            <AlertDescription className="text-green-800">
              Slides saved successfully! Slide ID: {saveResponse.id}
            </AlertDescription>
          </Alert>
        )}

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
                              const imageData = templateImages[
                                templateName
                              ] || {
                                imageUrl: null,
                                loading: true,
                                error: null,
                              };

                              const isLoading =
                                imageData.loading || loadingImages;
                              const imageUrl = imageData.imageUrl;
                              const imageError = imageData.error;

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
                                      src={
                                        "http://localhost:8000/image/" +
                                          imageUrl || "/placeholder.svg"
                                      }
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
                    </TabsContent>
                    <TabsContent value="upload">
                      <div className="border-2 border-dashed border-gray-300 rounded-lg p-8 text-center">
                        <Upload className="w-12 h-12 text-gray-400 mx-auto mb-4" />
                        <p className="text-gray-600 mb-4">
                          Upload your .pptx template
                        </p>
                        <input
                          type="file"
                          accept=".pptx"
                          onChange={handleTemplateUpload}
                          className="hidden"
                          id="template-file"
                        />
                        <label htmlFor="template-file">
                          <Button variant="outline" asChild>
                            <span>
                              <Upload className="w-4 h-4 mr-2" />
                              Choose File
                            </span>
                          </Button>
                        </label>
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
                        <Label htmlFor="slide-title">Slide Title</Label>
                        <Textarea
                          id="slide-title"
                          placeholder="Enter presentation title..."
                          value={slideTitle}
                          onChange={(e) => setSlideTitle(e.target.value)}
                          rows={2}
                        />
                      </div>
                      <div>
                        <Label htmlFor="topic">Presentation Content</Label>
                        <Textarea
                          id="topic"
                          placeholder="Enter your presentation topic or key points..."
                          value={topic}
                          onChange={(e) => setTopic(e.target.value)}
                          rows={4}
                        />
                      </div>
                      <div>
                        <Label htmlFor="purpose">Purpose</Label>
                        <Textarea
                          id="purpose"
                          placeholder="What is the purpose of this presentation?"
                          value={purpose}
                          onChange={(e) => setPurpose(e.target.value)}
                          rows={2}
                        />
                      </div>
                      <div>
                        <Label htmlFor="duration">Duration (minutes)</Label>
                        <input
                          type="number"
                          id="duration"
                          value={duration}
                          onChange={(e) => setDuration(Number(e.target.value))}
                          className="w-full p-2 border rounded"
                          min="1"
                          max="120"
                        />
                      </div>
                      <div>
                        <Label htmlFor="output-name">Output File Name</Label>
                        <input
                          type="text"
                          id="output-name"
                          value={outputFileName}
                          onChange={(e) => setOutputFileName(e.target.value)}
                          placeholder="Enter output filename (optional)"
                          className="w-full p-2 border rounded"
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
                  selectedTemplate === null ||
                  (!topic && !contentFile) ||
                  isGenerating
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
            <div className="mb-6">
              <h2 className="text-xl font-semibold mb-2">Generated Slides</h2>
              <div className="flex items-center gap-4 text-sm text-gray-600">
                <p>Session ID: {sessionId}</p>
                {saveResponse && (
                  <Badge className="bg-green-100 text-green-800">
                    Saved to Database (ID: {saveResponse.id})
                  </Badge>
                )}
              </div>
            </div>

            <div className="flex flex-col gap-14 items-center">
              {generatedSlides.map((slide, index) => (
                <Card
                  key={slide.id}
                  className="cursor-pointer hover:shadow-lg transition-shadow w-full max-w-5xl"
                  onClick={() => handleSlideEdit(slide.id)}
                >
                  <CardContent className="p-0">
                    <div className="relative">
                      <img
                        src={slide.thumbnail}
                        alt={slide.title}
                        className="w-full h-[600px] object-cover rounded"
                        onError={(e) => {
                          (e.target as HTMLImageElement).src =
                            "/placeholder.svg";
                        }}
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
            {selectedSlide !== null && (
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
