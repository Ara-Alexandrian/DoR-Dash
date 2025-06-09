from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.middleware.cors import CORSMiddleware
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

# Set up CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allow all methods
    allow_headers=["*"],  # Allow all headers
)

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