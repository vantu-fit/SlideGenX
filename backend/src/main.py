from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
import uvicorn
import os
from pathlib import Path
from api.auth import router as auth_router
from api.slide import router as slide_router

app = FastAPI(title="Portfolio Management API", version="1.0.0")

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth_router, prefix="/api/auth", tags=["auth"])
app.include_router(slide_router, prefix="/api/slide", tags=["slide"])

@app.get("/")
def read_root():
    return {"message": "Welcome to the Portfolio Management API"}

@app.get("/image/{file_path:path}")
async def get_image(file_path: str):
    """
    Serve images from the slides directory.
    Supports nested directories and various image formats.
    """
    # Define the base directory for images
    image_dir = Path("slides")
    
    # Security: Prevent directory traversal attacks
    if ".." in file_path:
        raise HTTPException(status_code=400, detail="Invalid file path")
    
    # Construct the full path
    image_path = image_dir / file_path
    
    # Check if file exists
    if not image_path.exists() or not image_path.is_file():
        raise HTTPException(status_code=404, detail="Image not found")
    
    # Check if it's actually in the slides directory (additional security)
    try:
        image_path.resolve().relative_to(image_dir.resolve())
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid file path")
    
    # Determine media type based on file extension
    file_extension = image_path.suffix.lower()
    media_type_map = {
        ".png": "image/png",
        ".jpg": "image/jpeg", 
        ".jpeg": "image/jpeg",
        ".gif": "image/gif",
        ".webp": "image/webp",
        ".svg": "image/svg+xml"
    }
    
    media_type = media_type_map.get(file_extension, "application/octet-stream")
    
    return FileResponse(
        path=str(image_path),
        media_type=media_type,
        filename=Path(file_path).name  # Use just the filename for download
    )

    
    # Determine media type based on file extension
    file_extension = image_path.suffix.lower()
    media_type_map = {
        ".png": "image/png",
        ".jpg": "image/jpeg", 
        ".jpeg": "image/jpeg",
        ".gif": "image/gif",
        ".webp": "image/webp",
        ".svg": "image/svg+xml"
    }
    
    media_type = media_type_map.get(file_extension, "application/octet-stream")
    
    return FileResponse(
        path=str(image_path),
        media_type=media_type,
        filename=filename
    )

@app.get("/health")
async def health_check():
    """Health check endpoint for monitoring"""
    return {"status": "healthy", "service": "Portfolio Management API"}

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="localhost",
        port=8000,
        reload=True,
        log_level="info"
    )