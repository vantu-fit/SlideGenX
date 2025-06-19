"use client"

import { useState } from "react"
import { Button } from "@/components/ui/button"
import { Card, CardContent } from "@/components/ui/card"
import { Input } from "@/components/ui/input"
import { Badge } from "@/components/ui/badge"
import { Search, Star } from "lucide-react"

// Mock templates data
const mockTemplates = [
  {
    id: 1,
    title: "Business Presentation",
    thumbnail: "/placeholder.svg?height=200&width=300",
    category: "Business",
    isPremium: false,
    rating: 4.8,
    downloads: 1250,
  },
  {
    id: 2,
    title: "Academic Report",
    thumbnail: "/placeholder.svg?height=200&width=300",
    category: "Education",
    isPremium: false,
    rating: 4.6,
    downloads: 890,
  },
  {
    id: 3,
    title: "Marketing Pitch",
    thumbnail: "/placeholder.svg?height=200&width=300",
    category: "Marketing",
    isPremium: true,
    rating: 4.9,
    downloads: 2100,
  },
  {
    id: 4,
    title: "Project Proposal",
    thumbnail: "/placeholder.svg?height=200&width=300",
    category: "Business",
    isPremium: false,
    rating: 4.7,
    downloads: 1560,
  },
  {
    id: 5,
    title: "Creative Portfolio",
    thumbnail: "/placeholder.svg?height=200&width=300",
    category: "Creative",
    isPremium: true,
    rating: 4.8,
    downloads: 780,
  },
  {
    id: 6,
    title: "Financial Report",
    thumbnail: "/placeholder.svg?height=200&width=300",
    category: "Finance",
    isPremium: false,
    rating: 4.5,
    downloads: 650,
  },
  {
    id: 7,
    title: "Startup Pitch Deck",
    thumbnail: "/placeholder.svg?height=200&width=300",
    category: "Business",
    isPremium: true,
    rating: 4.9,
    downloads: 3200,
  },
  {
    id: 8,
    title: "Training Materials",
    thumbnail: "/placeholder.svg?height=200&width=300",
    category: "Education",
    isPremium: false,
    rating: 4.4,
    downloads: 920,
  },
]

const categories = ["All", "Business", "Education", "Marketing", "Creative", "Finance"]

export function TemplatesTab() {
  const [searchTerm, setSearchTerm] = useState("")
  const [selectedCategory, setSelectedCategory] = useState("All")

  const filteredTemplates = mockTemplates.filter((template) => {
    const matchesSearch = template.title.toLowerCase().includes(searchTerm.toLowerCase())
    const matchesCategory = selectedCategory === "All" || template.category === selectedCategory
    return matchesSearch && matchesCategory
  })

  const handleSelectTemplate = (templateId: number) => {
    // In a real app, this would navigate to create page with selected template
    console.log("Selected template:", templateId)
  }

  return (
    <div className="space-y-6">
      {/* Search and Categories */}
      <div className="space-y-4">
        <div className="relative max-w-md">
          <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 w-4 h-4" />
          <Input
            placeholder="Search templates..."
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
                  <img
                    src={template.thumbnail || "/placeholder.svg"}
                    alt={template.title}
                    className="w-full h-40 object-cover rounded-t-lg"
                  />
                  {template.isPremium && (
                    <Badge className="absolute top-2 right-2 bg-gradient-to-r from-yellow-400 to-orange-500">
                      Premium
                    </Badge>
                  )}
                  <div className="absolute inset-0 bg-black bg-opacity-0 group-hover:bg-opacity-20 transition-all rounded-t-lg flex items-center justify-center">
                    <Button className="opacity-0 group-hover:opacity-100 transition-opacity" size="sm">
                      Use Template
                    </Button>
                  </div>
                </div>
                <div className="p-4">
                  <div className="flex items-start justify-between mb-2">
                    <h3 className="font-semibold line-clamp-1 flex-1">{template.title}</h3>
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
                  <p className="text-xs text-gray-500 mt-1">{template.downloads.toLocaleString()} downloads</p>
                </div>
              </CardContent>
            </Card>
          ))}
        </div>
      ) : (
        <div className="text-center py-12">
          <p className="text-gray-600">No templates found matching your criteria.</p>
        </div>
      )}
    </div>
  )
}
