from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from api.auth import router as auth_router
from api.slide import router as slide_router
import uvicorn
from core.config import settings


app = FastAPI(title="Portfolio Management API", version="1.0.0")
# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Adjust this to your frontend's URL in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
# Include routers
app.include_router(auth_router, prefix="/api/auth", tags=["auth"])
app.include_router(slide_router, prefix="/api/slide", tags=["slide"])
@app.get("/")
def read_root():
    return {"message": "Welcome to the Portfolio Management API"}

if __name__ == "__main__":
    uvicorn.run("main:app", host="localhost", port=8000, reload=True, log_level="info")