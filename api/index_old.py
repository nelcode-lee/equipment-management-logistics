"""
Vercel-optimized main.py for Equipment Management Logistics API
"""
import os
import sys
from pathlib import Path

# Add src directory to Python path
current_dir = Path(__file__).parent
src_dir = current_dir / "src"
sys.path.insert(0, str(src_dir))

# Load environment variables
from dotenv import load_dotenv
load_dotenv()

# Import the FastAPI app
try:
    from src.api.main import app
except ImportError as e:
    print(f"Import error: {e}")
    # Fallback: create a simple app
    from fastapi import FastAPI
    app = FastAPI()
    
    @app.get("/")
    async def root():
        return {"message": "API is running but imports failed", "error": str(e)}
    
    @app.get("/health")
    async def health():
        return {"status": "ok", "error": str(e)}

# This is the entry point for Vercel
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
