import os
from typing import List

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.db.database import init_db
from src.models.schemas import (
    HealthResponse,
    LoginRequest,
    LoginResponse,
)
from src.routers import users, profiles, posts, analytics, admin

# PUBLIC_INTERFACE
def create_app() -> FastAPI:
    """
    PUBLIC_INTERFACE
    Create and configure the FastAPI application with:
    - Metadata and OpenAPI tags
    - CORS using environment variables
    - Routers for health, users, profiles, posts, analytics, and admin
    - Startup event to initialize SQLite database

    Environment variables:
    - CORS_ALLOW_ORIGINS: Comma separated list of origins to allow for CORS (e.g., "http://localhost:3000,https://example.com")

    Returns:
        FastAPI: Configured FastAPI app instance.
    """
    app = FastAPI(
        title="Social Media Backend API",
        description="Backend API for social media dashboard with users, profiles, posts, analytics, and admin endpoints.",
        version="1.0.0",
        openapi_tags=[
            {"name": "health", "description": "Health and meta endpoints."},
            {"name": "auth", "description": "Authentication endpoints (demo placeholder)."},
            {"name": "users", "description": "User management endpoints."},
            {"name": "profiles", "description": "User profile endpoints."},
            {"name": "posts", "description": "Post and engagement endpoints."},
            {"name": "analytics", "description": "Analytics endpoints for posts and followers."},
            {"name": "admin", "description": "Administrative endpoints for platform-level analytics."},
        ],
    )

    # CORS configuration from environment
    cors_origins_env = os.getenv("CORS_ALLOW_ORIGINS", "*")
    allow_origins: List[str]
    if cors_origins_env.strip() == "*":
        allow_origins = ["*"]
    else:
        allow_origins = [o.strip() for o in cors_origins_env.split(",") if o.strip()]

    app.add_middleware(
        CORSMiddleware,
        allow_origins=allow_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Health route
    @app.get("/", tags=["health"], summary="Health Check", operation_id="health_check")
    # PUBLIC_INTERFACE
    def health_check() -> HealthResponse:
        """Return a simple health status payload."""
        return HealthResponse(status="ok")

    # Demo login placeholder (no real security; for demo/testing only)
    @app.post("/auth/login", tags=["auth"], summary="Demo login", operation_id="auth_login")
    # PUBLIC_INTERFACE
    def login(payload: LoginRequest):
        """
        Demo login endpoint.

        Accepts any email/password and returns a demo session token for testing.
        DO NOT USE IN PRODUCTION.

        Request:
            LoginRequest: email and password.
        Returns:
            LoginResponse: contains a demo session token and user email.
        """
        # extremely naive "token"
        token = f"demo-token:{payload.email}"
        return LoginResponse(token=token, email=payload.email)

    # Include routers
    app.include_router(users.router)
    app.include_router(profiles.router)
    app.include_router(posts.router)
    app.include_router(analytics.router)
    app.include_router(admin.router)

    # Initialize DB on startup
    @app.on_event("startup")
    async def on_startup():
        init_db()

    return app


# Instantiate the application for ASGI servers
app = create_app()
