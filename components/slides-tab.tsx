"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { Button } from "@/components/ui/button";
import { Card, CardContent } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Badge } from "@/components/ui/badge";
import { useRouter } from "next/navigation";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";
import {
  Search,
  Filter,
  MoreVertical,
  Edit,
  Trash2,
  Download,
  Plus,
  LogIn,
} from "lucide-react";
import { useGetSlideIds } from "@/hooks/use-get-slides";
import { useAuth } from "@/hooks/use-auth"; // Add this import

// Mock slides data (keep as fallback)
const mockSlides = [
  {
    id: 1,
    title: "Q4 Business Review",
    thumbnail: "/placeholder.svg?height=200&width=300",
    createdAt: "2024-01-15",
    slideCount: 12,
  },
  {
    id: 2,
    title: "Marketing Strategy 2024",
    thumbnail: "/placeholder.svg?height=200&width=300",
    createdAt: "2024-01-10",
    slideCount: 8,
  },
  {
    id: 3,
    title: "Product Launch Presentation",
    thumbnail: "/placeholder.svg?height=200&width=300",
    createdAt: "2024-01-08",
    slideCount: 15,
  },
  {
    id: 4,
    title: "Team Training Materials",
    thumbnail: "/placeholder.svg?height=200&width=300",
    createdAt: "2024-01-05",
    slideCount: 20,
  },
  {
    id: 5,
    title: "Client Proposal",
    thumbnail: "/placeholder.svg?height=200&width=300",
    createdAt: "2024-01-03",
    slideCount: 10,
  },
  {
    id: 6,
    title: "Annual Report Summary",
    thumbnail: "/placeholder.svg?height=200&width=300",
    createdAt: "2024-01-01",
    slideCount: 6,
  },
];

export function SlidesTab() {
  const router = useRouter();
  const [searchTerm, setSearchTerm] = useState("");
  const [sortBy, setSortBy] = useState("date");
  
  // Use authentication hook
  const { isAuthenticated, isLoading: authLoading, user } = useAuth();
  const { slideIds, isLoading, error, fetchSlideIds, reset } = useGetSlideIds();

  // Only fetch slides when user is authenticated
  useEffect(() => {
    if (isAuthenticated && !authLoading) {
      fetchSlideIds();
    }
  }, [isAuthenticated, authLoading, fetchSlideIds]);

  console.log("Auth status:", { isAuthenticated, user, slideIds });

  // Handle authentication loading
  if (authLoading) {
    return (
      <div className="flex items-center justify-center py-12">
        <div className="text-center">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600 mx-auto mb-4"></div>
          <p className="text-gray-600">Loading...</p>
        </div>
      </div>
    );
  }

  // Handle unauthenticated state
  if (!isAuthenticated) {
    return (
      <div className="space-y-6">
        <div className="text-center py-12">
          <div className="w-16 h-16 bg-gray-100 rounded-full flex items-center justify-center mx-auto mb-4">
            <LogIn className="w-8 h-8 text-gray-400" />
          </div>
          <h3 className="text-lg font-semibold mb-2">Authentication Required</h3>
          <p className="text-gray-600 mb-4">
            Please log in to view and manage your slides.
          </p>
          <Button onClick={() => router.push('/login')} className="mr-2">
            Log In
          </Button>
          <Button variant="outline" onClick={() => router.push('/register')}>
            Sign Up
          </Button>
        </div>
      </div>
    );
  }

  // Handle API loading
  if (isLoading) {
    return (
      <div className="space-y-6">
        <div className="flex items-center justify-center py-12">
          <div className="text-center">
            <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600 mx-auto mb-4"></div>
            <p className="text-gray-600">Loading your slides...</p>
          </div>
        </div>
      </div>
    );
  }

  // Handle API error
  if (error) {
    return (
      <div className="space-y-6">
        <div className="text-center py-12">
          <div className="w-16 h-16 bg-red-100 rounded-full flex items-center justify-center mx-auto mb-4">
            <Trash2 className="w-8 h-8 text-red-600" />
          </div>
          <h3 className="text-lg font-semibold mb-2">Error Loading Slides</h3>
          <p className="text-red-600 mb-4">{error}</p>
          <Button onClick={() => fetchSlideIds()} variant="outline">
            Try Again
          </Button>
        </div>
      </div>
    );
  }

  const filteredSlides = mockSlides
    .filter((slide) =>
      slide.title.toLowerCase().includes(searchTerm.toLowerCase())
    )
    .sort((a, b) => {
      if (sortBy === "date") {
        return (
          new Date(b.createdAt).getTime() - new Date(a.createdAt).getTime()
        );
      } else if (sortBy === "title") {
        return a.title.localeCompare(b.title);
      }
      return 0;
    });

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString("en-US", {
      year: "numeric",
      month: "short",
      day: "numeric",
    });
  };

  return (
    <div className="space-y-6">
      {/* Welcome message */}
      <div className="bg-blue-50 p-4 rounded-lg">
        <h2 className="text-lg font-semibold text-blue-900">
          Welcome back, {user?.full_name || user?.username}!
        </h2>
        <p className="text-blue-700">
          You have {slideIds.length} slide{slideIds.length !== 1 ? 's' : ''} in your collection.
        </p>
      </div>

      {/* Search and Filters */}
      <div className="flex flex-col sm:flex-row gap-4 items-start sm:items-center justify-between">
        <div className="relative flex-1 max-w-md">
          <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 w-4 h-4" />
          <Input
            placeholder="Search slides..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            className="pl-10"
          />
        </div>
        <div className="flex items-center space-x-2">
          <DropdownMenu>
            <DropdownMenuTrigger asChild>
              <Button variant="outline" size="sm">
                <Filter className="w-4 h-4 mr-2" />
                Sort by {sortBy === "date" ? "Date" : "Title"}
              </Button>
            </DropdownMenuTrigger>
            <DropdownMenuContent>
              <DropdownMenuItem onClick={() => setSortBy("date")}>
                Sort by Date
              </DropdownMenuItem>
              <DropdownMenuItem onClick={() => setSortBy("title")}>
                Sort by Title
              </DropdownMenuItem>
            </DropdownMenuContent>
          </DropdownMenu>
        </div>
      </div>

      {/* Create New Slide Card */}
      <Link href="/create">
        <Card className="border-2 border-dashed border-gray-300 hover:border-blue-500 transition-colors cursor-pointer">
          <CardContent className="flex flex-col items-center justify-center py-12">
            <div className="w-16 h-16 bg-blue-100 rounded-full flex items-center justify-center mb-4">
              <Plus className="w-8 h-8 text-blue-600" />
            </div>
            <h3 className="text-lg font-semibold mb-2">Create New Slide</h3>
            <p className="text-gray-600 text-center">
              Start creating amazing presentations with AI
            </p>
          </CardContent>
        </Card>
      </Link>

      {/* Slides Grid */}
      {slideIds.length > 0 ? (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {slideIds.map((slide, index) => (
            <Card
              onClick={() => {
                router.push(`/slide/${slide}`);
              }}
              key={index}
              className="group hover:shadow-lg transition-shadow cursor-pointer"
            >
              <CardContent className="p-0">
                <div className="relative">
                  <img
                    src={`http://localhost:8000/image/${slide}/images/page_1.png`}
                    alt={slide}
                    className="w-full h-48 object-cover rounded-t-lg"
                    onError={(e) => {
                      // Fallback to placeholder if image fails to load
                      e.currentTarget.src = "/placeholder.svg?height=200&width=300";
                    }}
                  />
                  <div className="absolute top-2 right-2 opacity-0 group-hover:opacity-100 transition-opacity">
                    <DropdownMenu>
                      <DropdownMenuTrigger asChild>
                        <Button size="sm" variant="secondary">
                          <MoreVertical className="w-4 h-4" />
                        </Button>
                      </DropdownMenuTrigger>
                      <DropdownMenuContent>
                        <DropdownMenuItem>
                          <Edit className="w-4 h-4 mr-2" />
                          Edit
                        </DropdownMenuItem>
                        <DropdownMenuItem>
                          <Download className="w-4 h-4 mr-2" />
                          Download
                        </DropdownMenuItem>
                        <DropdownMenuItem className="text-red-600">
                          <Trash2 className="w-4 h-4 mr-2" />
                          Delete
                        </DropdownMenuItem>
                      </DropdownMenuContent>
                    </DropdownMenu>
                  </div>
                </div>
                <div className="p-4">
                  <h3 className="font-semibold mb-2 line-clamp-1">
                    {slide}
                  </h3>
                  <div className="flex items-center justify-between text-sm text-gray-500">
                    <span>Session ID</span>
                    <Badge variant="secondary" className="text-xs">
                      {slide.slice(0, 8)}...
                    </Badge>
                  </div>
                </div>
              </CardContent>
            </Card>
          ))}
        </div>
      ) : (
        <div className="text-center py-12">
          <div className="w-16 h-16 bg-gray-100 rounded-full flex items-center justify-center mx-auto mb-4">
            <Plus className="w-8 h-8 text-gray-400" />
          </div>
          <h3 className="text-lg font-semibold mb-2">No Slides Yet</h3>
          <p className="text-gray-600 mb-4">
            Start creating your first presentation to see it here.
          </p>
          <Button onClick={() => router.push('/create')}>
            Create Your First Slide
          </Button>
        </div>
      )}
    </div>
  );
}