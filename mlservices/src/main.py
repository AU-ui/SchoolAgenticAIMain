from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
from contextlib import asynccontextmanager

# Import routers with error handling
try:
    from src.api.teacher_ml import router as teacher_router
    TEACHER_ML_AVAILABLE = True
except ImportError as e:
    print(f"⚠️ Teacher ML router not available: {e}")
    TEACHER_ML_AVAILABLE = False

try:
    from src.api.parent_ml import router as parent_router
    PARENT_ML_AVAILABLE = True
except ImportError as e:
    print(f"⚠️ Parent ML router not available: {e}")
    PARENT_ML_AVAILABLE = False

try:
    from src.free_ai_endpoints import router as free_ai_router
    FREE_AI_AVAILABLE = True
except ImportError as e:
    print(f"⚠️ Free AI router not available: {e}")
    FREE_AI_AVAILABLE = False

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    print("🚀 Starting ML Services for EdTech Platform...")
    print(f"📊 Teacher Analytics: {'✅ Loaded' if TEACHER_ML_AVAILABLE else '❌ Not Available'}")
    print(f"👨‍👩‍👧‍👦 Parent Analytics: {'✅ Loaded' if PARENT_ML_AVAILABLE else '❌ Not Available'}")
    print(f"🆓 Free AI Services: {'✅ Loaded' if FREE_AI_AVAILABLE else '❌ Not Available'}")
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

# Include routers only if available
if TEACHER_ML_AVAILABLE:
    app.include_router(teacher_router)
    print("✅ Teacher ML router included")

if PARENT_ML_AVAILABLE:
    app.include_router(parent_router, prefix="/api")
    print("✅ Parent ML router included")

if FREE_AI_AVAILABLE:
    app.include_router(free_ai_router)
    print("✅ Free AI router included")

@app.get("/")
async def root():
    return {
        "message": "EdTech Platform ML Services",
        "version": "1.0.0",
        "services": {
            "teacher_analytics": "✅ Active" if TEACHER_ML_AVAILABLE else "❌ Not Available",
            "parent_analytics": "✅ Active" if PARENT_ML_AVAILABLE else "❌ Not Available",
            "free_ai_services": "✅ Active" if FREE_AI_AVAILABLE else "❌ Not Available"
        }
    }

@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "services": {
            "teacher_ml": "operational" if TEACHER_ML_AVAILABLE else "not available",
            "parent_ml": "operational" if PARENT_ML_AVAILABLE else "not available",
            "free_ai": "operational" if FREE_AI_AVAILABLE else "not available"
        },
        "timestamp": "2024-01-01T00:00:00Z"
    }

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000) 