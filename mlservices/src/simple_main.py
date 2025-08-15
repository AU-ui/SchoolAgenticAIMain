from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

# Import the simple free AI endpoints
from simple_free_ai_endpoints import router as free_ai_router

app = FastAPI(
    title="Simple ML Services",
    description="Simple ML Services for Testing",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include only the free AI router
app.include_router(free_ai_router)

@app.get("/")
async def root():
    return {
        "message": "Simple ML Services Running",
        "version": "1.0.0",
        "endpoints": {
            "free_ai_reports": "/ml/free-ai/reports/generate",
            "free_ai_lesson_plans": "/ml/free-ai/lesson-plans/generate",
            "free_ai_assignments": "/ml/free-ai/assignments/generate",
            "free_ai_capabilities": "/ml/free-ai/capabilities"
        }
    }

@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "service": "Simple ML Services",
        "timestamp": "2024-01-01T00:00:00Z"
    }

if __name__ == "__main__":
    print("🚀 Starting Simple ML Services...")
    print("📍 Server will be available at: http://localhost:8000")
    print("🔍 Health check: http://localhost:8000/health")
    print("📊 Free AI Reports: http://localhost:8000/ml/free-ai/reports/generate")
    
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)
