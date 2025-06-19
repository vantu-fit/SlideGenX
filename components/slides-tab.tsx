"use client"

import { useState } from "react"
import Link from "next/link"
import { Button } from "@/components/ui/button"
import { Card, CardContent } from "@/components/ui/card"
import { Input } from "@/components/ui/input"
import { Badge } from "@/components/ui/badge"
import { DropdownMenu, DropdownMenuContent, DropdownMenuItem, DropdownMenuTrigger } from "@/components/ui/dropdown-menu"
import { Search, Filter, MoreVertical, Edit, Trash2, Download, Plus } from "lucide-react"

// Mock slides data
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
]

export function SlidesTab() {
  const [searchTerm, setSearchTerm] = useState("")
  const [sortBy, setSortBy] = useState("date")

  const filteredSlides = mockSlides
    .filter((slide) => slide.title.toLowerCase().includes(searchTerm.toLowerCase()))
    .sort((a, b) => {
      if (sortBy === "date") {
        return new Date(b.createdAt).getTime() - new Date(a.createdAt).getTime()
      } else if (sortBy === "title") {
        return a.title.localeCompare(b.title)
      }
      return 0
    })

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString("en-US", {
      year: "numeric",
      month: "short",
      day: "numeric",
    })
  }

  return (
    <div className="space-y-6">
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
              <DropdownMenuItem onClick={() => setSortBy("date")}>Sort by Date</DropdownMenuItem>
              <DropdownMenuItem onClick={() => setSortBy("title")}>Sort by Title</DropdownMenuItem>
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
            <p className="text-gray-600 text-center">Start creating amazing presentations with AI</p>
          </CardContent>
        </Card>
      </Link>

      {/* Slides Grid */}
      {filteredSlides.length > 0 ? (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {filteredSlides.map((slide) => (
            <Card key={slide.id} className="group hover:shadow-lg transition-shadow cursor-pointer">
              <CardContent className="p-0">
                <div className="relative">
                  <img
                    src={slide.thumbnail || "/placeholder.svg"}
                    alt={slide.title}
                    className="w-full h-48 object-cover rounded-t-lg"
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
                  <Badge className="absolute bottom-2 left-2">{slide.slideCount} slides</Badge>
                </div>
                <div className="p-4">
                  <h3 className="font-semibold mb-2 line-clamp-1">{slide.title}</h3>
                  <p className="text-sm text-gray-600">Created {formatDate(slide.createdAt)}</p>
                </div>
              </CardContent>
            </Card>
          ))}
        </div>
      ) : (
        <div className="text-center py-12">
          <p className="text-gray-600">No slides found matching your search.</p>
        </div>
      )}
    </div>
  )
}
