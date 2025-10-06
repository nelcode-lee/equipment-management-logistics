#!/usr/bin/env python3
"""
Main orchestrator for the Equipment Tracking System
"""
import uvicorn
import sys
import os

# Add src to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.config import settings
from src.api.main import app

def main():
    """Run the FastAPI application"""
    print("🚀 Starting Equipment Tracking System...")
    print(f"📊 API Documentation: http://{settings.HOST}:{settings.PORT}/docs")
    print(f"🔍 Health Check: http://{settings.HOST}:{settings.PORT}/health")
    print(f"🌐 API Base URL: http://{settings.HOST}:{settings.PORT}")
    
    uvicorn.run(
        app,
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG,
        log_level="info" if not settings.DEBUG else "debug"
    )

if __name__ == "__main__":
    main()

