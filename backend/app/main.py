from fastapi import FastAPI, HTTPException, Depends, status, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.responses import RedirectResponse

from app.core.config import settings
from app.api.api import api_router
# Import the relationship setup function
from app.db.setup import setup_relationships

app = FastAPI(
    title="DoR-Dash API",
    description="API for the Dose of Reality Dashboard",
    version="0.1.0",
    docs_url="/docs",  # Make Swagger UI accessible at /docs
    redoc_url="/redoc",  # Make ReDoc accessible at /redoc
    openapi_url="/openapi.json",  # OpenAPI schema
    # Set max upload size to 50MB
    max_request_size=50 * 1024 * 1024  # 50MB in bytes
)

# Add trusted host middleware for security
app.add_middleware(
    TrustedHostMiddleware, 
    allowed_hosts=["dd.kronisto.net", "172.30.98.21", "172.30.98.177", "localhost", "127.0.0.1", "*.kronisto.net"]
)

# Set up CORS for reverse proxy compatibility
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://dd.kronisto.net",
        "http://172.30.98.21:1717",
        "http://localhost:1717",
        "http://127.0.0.1:1717"
    ],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)

# Add reverse proxy header handling middleware
@app.middleware("http")
async def proxy_headers_middleware(request: Request, call_next):
    """Handle reverse proxy headers for proper client detection and protocol handling"""
    # Handle X-Forwarded-Proto for HTTPS detection
    if "x-forwarded-proto" in request.headers:
        request.scope["scheme"] = request.headers["x-forwarded-proto"]
    
    # Handle X-Forwarded-Host for proper host detection
    if "x-forwarded-host" in request.headers:
        request.scope["server"] = (request.headers["x-forwarded-host"], None)
    
    # Handle X-Real-IP or X-Forwarded-For for client IP detection
    if "x-real-ip" in request.headers:
        request.scope["client"] = (request.headers["x-real-ip"], 0)
    elif "x-forwarded-for" in request.headers:
        # Get the first IP from X-Forwarded-For (original client)
        client_ip = request.headers["x-forwarded-for"].split(",")[0].strip()
        request.scope["client"] = (client_ip, 0)
    
    response = await call_next(request)
    return response

# We're using a simplified auth system for now
# setup_relationships()

# Include API router
app.include_router(api_router, prefix=settings.API_V1_STR)


@app.get("/", include_in_schema=False)
async def root():
    """Redirect root to documentation"""
    return RedirectResponse(url="/docs")


@app.get("/health", tags=["health"])
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "message": "DoR-Dash API is running"}

@app.get("/api/v1/health", tags=["health"])
async def health_check_v1():
    """Health check endpoint under API v1 prefix"""
    return {"status": "healthy", "message": "DoR-Dash API is running"}