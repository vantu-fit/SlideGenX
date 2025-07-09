from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, FileResponse
from api.auth import router as auth_router
from api.slide import router as slide_router
import uvicorn
from core.config import settings


app = FastAPI(title="Portfolio Management API", version="1.0.0")
# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # <-- sửa tại đây
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
# app.include_router(auth_router, prefix="/api/auth", tags=["auth"])
# app.include_router(slide_router, prefix="/api/slide", tags=["slide"])
@app.get("/")
def read_root():
    return {"message": "Welcome to the Portfolio Management API"}

@app.get("/image{path:path}", response_class=FileResponse)
def get_image(path: str):
    """
    Serve an image file from the 'images' directory.
    """
    import os
    from fastapi.responses import FileResponse
    import logging
    image_path = path
    logging.error(f"Image path: {image_path}")
    if not os.path.exists(image_path):
        return {"error": "Image not found"}, 404
    return FileResponse(image_path, media_type="image/png")

if __name__ == "__main__":
    uvicorn.run("main:app", host="localhost", port=8000, reload=True, log_level="info")