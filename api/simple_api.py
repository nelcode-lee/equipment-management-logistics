"""
Simple API entry point for Vercel deployment
"""
import os
import sys
from pathlib import Path

# Add local src directory to Python path
current_dir = Path(__file__).parent
src_dir = current_dir / "src"
sys.path.insert(0, str(src_dir))

from fastapi import FastAPI, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.base import BaseHTTPMiddleware

# Custom middleware for mobile support
class MobileSupportMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        response = await call_next(request)
        
        # Add mobile-specific headers
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        
        # Ensure CORS headers are present for all origins (mobile compatibility)
        origin = request.headers.get("origin")
        if origin:
            response.headers["Access-Control-Allow-Origin"] = "*"
            response.headers["Access-Control-Allow-Methods"] = "GET, POST, PUT, DELETE, OPTIONS, PATCH, HEAD"
            response.headers["Access-Control-Allow-Headers"] = "*"
            response.headers["Access-Control-Expose-Headers"] = "*"
        
        return response

# Create a minimal FastAPI app
app = FastAPI(title="Equipment Management API", version="1.0.0")

# Add mobile support middleware
app.add_middleware(MobileSupportMiddleware)

# Add CORS middleware with wildcard support for mobile
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins for mobile compatibility
    allow_credentials=False,  # Must be False when using wildcard origins
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS", "PATCH", "HEAD"],
    allow_headers=["*"],  # Allow all headers for mobile
    expose_headers=["*"],
    max_age=3600
)

@app.get("/")
async def root():
    return {"message": "Equipment Management API is running!", "status": "ok"}

@app.get("/health")
async def health():
    import os
    db_url = os.getenv("DATABASE_URL", "not set")
    # Mask the password for security
    if ":" in db_url and "@" in db_url:
        parts = db_url.split("://")
        if len(parts) == 2:
            creds_and_rest = parts[1].split("@")
            if len(creds_and_rest) == 2:
                user_pass = creds_and_rest[0].split(":")
                if len(user_pass) == 2:
                    db_url = f"{parts[0]}://{user_pass[0]}:****@{creds_and_rest[1]}"
    
    return {
        "status": "healthy",
        "message": "API is working correctly",
        "database": db_url[:80] + "..." if len(db_url) > 80 else db_url
    }

@app.get("/mobile-test")
async def mobile_test(request: Request):
    """Test endpoint for mobile debugging"""
    return {
        "status": "mobile_test_ok",
        "user_agent": request.headers.get("user-agent", "unknown"),
        "origin": request.headers.get("origin", "unknown"),
        "host": request.headers.get("host", "unknown"),
        "cors_headers": {
            "access_control_allow_origin": request.headers.get("access-control-allow-origin"),
            "access_control_request_method": request.headers.get("access-control-request-method"),
            "access_control_request_headers": request.headers.get("access-control-request-headers")
        }
    }

@app.get("/test-login-page", response_class=Response)
async def test_login_page():
    """Simple HTML login page for mobile testing"""
    html_content = """
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Driver Login Test</title>
    <style>
        body { font-family: Arial, sans-serif; max-width: 500px; margin: 50px auto; padding: 20px; background: #f5f5f5; }
        .container { background: white; padding: 30px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }
        input { width: 100%; padding: 12px; margin: 10px 0; border: 1px solid #ddd; border-radius: 5px; font-size: 16px; box-sizing: border-box; }
        button { width: 100%; padding: 12px; background: #007bff; color: white; border: none; border-radius: 5px; font-size: 16px; cursor: pointer; margin-top: 10px; }
        button:hover { background: #0056b3; }
        #result { margin-top: 20px; padding: 15px; border-radius: 5px; display: none; }
        .success { background: #d4edda; border: 1px solid #c3e6cb; color: #155724; }
        .error { background: #f8d7da; border: 1px solid #f5c6cb; color: #721c24; }
    </style>
</head>
<body>
    <div class="container">
        <h1>🚛 Driver Login</h1>
        <form id="loginForm">
            <input type="text" id="username" placeholder="Username" value="driver1" required>
            <input type="password" id="password" placeholder="Password" value="Driver123" required>
            <button type="submit">Login</button>
        </form>
        <div id="result"></div>
    </div>
    <script>
        const API_URL = window.location.origin;
        document.getElementById('loginForm').addEventListener('submit', async (e) => {
            e.preventDefault();
            const resultDiv = document.getElementById('result');
            resultDiv.style.display = 'block';
            resultDiv.className = '';
            resultDiv.innerHTML = '⏳ Logging in...';
            try {
                const response = await fetch(API_URL + '/auth/login', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({
                        username: document.getElementById('username').value,
                        password: document.getElementById('password').value
                    })
                });
                const data = await response.json();
                if (response.ok) {
                    resultDiv.className = 'success';
                    resultDiv.innerHTML = '✅ Login Successful!<br>User: ' + data.user.full_name + '<br>Role: ' + data.user.role;
                    localStorage.setItem('token', data.access_token);
                    localStorage.setItem('user', JSON.stringify(data.user));
                    setTimeout(() => { window.location.href = 'https://equipment-driver-app.vercel.app'; }, 2000);
                } else {
                    resultDiv.className = 'error';
                    resultDiv.innerHTML = '❌ Login Failed: ' + (data.detail || JSON.stringify(data));
                }
            } catch (error) {
                resultDiv.className = 'error';
                resultDiv.innerHTML = '❌ Error: ' + error.message;
            }
        });
    </script>
</body>
</html>
    """
    return Response(content=html_content, media_type="text/html")

# Import and include all routes from the main app
try:
    # Import auth routes
    from src.api.auth import router as auth_router
    app.include_router(auth_router)
    print("✅ Auth routes imported successfully")
    
    # Import main app routes (equipment, movements, balances, etc.)
    from src.api.main import app as main_app
    # Copy all routes from main app except auth (already included)
    for route in main_app.routes:
        if not any(r.path == route.path for r in app.routes):
            app.routes.append(route)
    print("✅ Equipment routes imported successfully")
except Exception as e:
    print(f"❌ Error importing routes: {e}")
    # Create a basic auth endpoint for testing
    @app.post("/auth/login")
    async def basic_login():
        return {"error": "Auth service not available"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
