from fastapi import Depends, FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
import logging
from utils.logger_config import setup_logging
from routes import auth_routes, user_routes
from dependencies.container import get_app_config
from exceptions.custom_exceptions import AuthException, RateLimitExceeded
from security.rate_limiter import rate_limit_dependency

# Setup logging before anything else
setup_logging()
logger = logging.getLogger(__name__)

# Load app configuration
app_config = get_app_config()

app = FastAPI(
    title=app_config.APP_NAME,
    debug=app_config.DEBUG_MODE,
    description="A secure authentication service with LDAP and JWT.",
    version="1.0.0"
)

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # Adjust in production to specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)# Exception Handlers
@app.exception_handler(AuthException)
async def auth_exception_handler(request: Request, exc: AuthException):
    """Handles custom authentication-related exceptions."""
    logger.warning(f"AuthException caught for {request.url.path}: {exc.detail}")
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.detail}
    )

@app.exception_handler(RateLimitExceeded)
async def rate_limit_exception_handler(request: Request, exc: RateLimitExceeded):
    """Handles rate limit exceeded exceptions."""
    logger.warning(f"Rate limit exceeded for IP: {request.client.host} on {request.url.path}")
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.detail}
    )

@app.exception_handler(Exception)
async def generic_exception_handler(request: Request, exc: Exception):
    """Handles all unhandled exceptions."""
    logger.error(f"Unhandled exception for {request.url.path}: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={"detail": "An unexpected server error occurred."}
    )

# Include API routers
app.include_router(auth_routes.router)
app.include_router(user_routes.router, dependencies=[Depends(rate_limit_dependency)]) # Apply rate limit to user routes

@app.get("/", summary="Root endpoint for service status", response_model=dict)
async def read_root():
    """Returns a simple status message."""
    return {"message": f"{app_config.APP_NAME} is running!"}