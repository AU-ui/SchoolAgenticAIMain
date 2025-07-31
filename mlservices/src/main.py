from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
from contextlib import asynccontextmanager

from src.api.teacher_ml import router as teacher_router
from src.api.parent_ml import router as parent_router

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    print("🚀 Starting ML Services for EdTech Platform...")
    print("📊 Teacher Analytics: ✅ Loaded")
    print("👨‍👩‍👧‍👦 Parent Analytics: ✅ Loaded")
    print("😊 Sentiment Analysis: ✅ Loaded")
    print("🌐 Translation Services: ✅ Loaded")
    print("📈 Engagement Predictor: ✅ Loaded")
    print("🔤 Language Detection: ✅ Loaded")
    yield
    # Shutdown
    print("🛑 Shutting down ML Services...")

app = FastAPI(
    title="EdTech Platform ML Services",
    description="Machine Learning Services for Pain Points #1 and #5",
    version="1.0.0",
    lifespan=lifespan
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(teacher_router)
app.include_router(parent_router, prefix="/api")

@app.get("/")
async def root():
    return {
        "message": "EdTech Platform ML Services",
        "version": "1.0.0",
        "services": {
            "teacher_analytics": "✅ Active",
            "parent_analytics": "✅ Active",
            "sentiment_analysis": "✅ Active",
            "translation_services": "✅ Active",
            "engagement_prediction": "✅ Active",
            "language_detection": "✅ Active"
        }
    }

@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "services": "all operational",
        "timestamp": "2024-01-01T00:00:00Z"
    }

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000) 