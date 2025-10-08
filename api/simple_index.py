"""
Simple Vercel entry point for testing
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="Equipment Management API", version="1.0.0")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify your frontend URLs
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    return {"message": "Equipment Management API is running!", "status": "ok"}

@app.get("/health")
async def health():
    return {"status": "healthy", "message": "API is working correctly"}

@app.get("/test")
async def test():
    return {
        "message": "Test endpoint working",
        "environment": {
            "python_version": "3.11",
            "fastapi_version": "0.104.1"
        }
    }

# This is the entry point for Vercel
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
