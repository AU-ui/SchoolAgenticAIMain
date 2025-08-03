#!/usr/bin/env python3
"""
ML Services Server Startup Script
"""
import sys
import os

# Add the current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

if __name__ == "__main__":
    import uvicorn
    from src.main import app
    
    print("🚀 Starting ML Services Server...")
    print("📍 Server will be available at: http://localhost:8000")
    print("🔍 Health check: http://localhost:8000/health")
    
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    ) 