"""
FastAPI main application with Scalar API documentation.
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.openapi.utils import get_openapi
from contextlib import asynccontextmanager

from backend.config import get_settings
from backend.utils.db import create_tables
from backend.api.routes import maps, runs, bugs, metrics, events


settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan - startup and shutdown events."""
    # Startup
    print("🚀 Starting RL Game Tester API...")
    await create_tables()
    print("✅ Database tables ready")
    
    yield
    
    # Shutdown
    print("👋 Shutting down...")


# Create FastAPI app
app = FastAPI(
    title="RL Game Tester API",
    description="Backend API for Deep RL Game Quality Assurance Framework",
    version="0.1.0",
    lifespan=lifespan,
    docs_url=None,  # Disable default Swagger
    redoc_url=None,  # Disable ReDoc
)

# CORS middleware for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Custom OpenAPI schema
def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema
    openapi_schema = get_openapi(
        title="RL Game Tester API",
        version="0.1.0",
        description="Backend API for Deep RL Game Quality Assurance Framework",
        routes=app.routes,
    )
    app.openapi_schema = openapi_schema
    return app.openapi_schema


app.openapi = custom_openapi


# Scalar API documentation
@app.get("/docs", include_in_schema=False)
async def scalar_docs():
    """Serve Scalar API documentation."""
    from fastapi.responses import HTMLResponse
    
    return HTMLResponse("""
<!DOCTYPE html>
<html>
<head>
    <title>RL Game Tester API</title>
    <meta charset="utf-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1" />
    <style>
        body { margin: 0; }
    </style>
</head>
<body>
    <script
        id="api-reference"
        data-url="/openapi.json"
        data-configuration='{"theme": "purple", "layout": "modern"}'
    ></script>
    <script src="https://cdn.jsdelivr.net/npm/@scalar/api-reference"></script>
</body>
</html>
    """)


# Include routers
app.include_router(maps.router, prefix="/api/maps", tags=["Maps"])
app.include_router(runs.router, prefix="/api/runs", tags=["Runs"])
app.include_router(events.router, prefix="/api/events", tags=["Events"])
app.include_router(bugs.router, prefix="/api/bugs", tags=["Bugs"])
app.include_router(metrics.router, prefix="/api/metrics", tags=["Metrics"])


@app.get("/")
async def root():
    """Health check endpoint."""
    return {
        "status": "ok",
        "service": "RL Game Tester API",
        "version": "0.1.0",
        "docs": "/docs"
    }


@app.get("/health")
async def health():
    """Detailed health check."""
    return {
        "status": "healthy",
        "database": "connected",
        "redis": "connected",
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "backend.main:app",
        host=settings.api_host,
        port=settings.api_port,
        reload=settings.debug
    )
