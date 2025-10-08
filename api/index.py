"""
Minimal Vercel serverless entry point for Equipment Tracker API
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Create FastAPI app
app = FastAPI(title="Equipment Management API", version="1.0.0")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS", "PATCH", "HEAD"],
    allow_headers=["*"],
    expose_headers=["*"],
)

@app.get("/health")
def health():
    return {"status": "healthy", "message": "Equipment Tracker API is running"}

@app.get("/")
def root():
    return {"message": "Equipment Management API", "version": "1.0.0"}

# Vercel handler
handler = app