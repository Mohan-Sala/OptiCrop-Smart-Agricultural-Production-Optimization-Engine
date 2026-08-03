import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request, status
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException

from app.core.config import settings
from app.core.logging import setup_logging
from app.core.middleware import register_middlewares
from app.api.v1.router import api_router
from app.utils.exceptions import AppException
from app.utils.responses import error_response, success_response

logger = logging.getLogger("app.main")


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Initialize logging first
    setup_logging()
    logger.info("Initializing OptiCrop AI Backend Services...")
    yield
    logger.info("Shutting down OptiCrop AI Backend Services...")


app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="OptiCrop is an AI-powered Smart Agricultural Production Optimization Engine.",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
)

# Register all core middlewares
register_middlewares(app)

# Register API v1 router
app.include_router(api_router, prefix=settings.API_V1_PREFIX)


# --- Global Exception Handlers ---


@app.exception_handler(AppException)
async def custom_app_exception_handler(request: Request, exc: AppException):
    """Handler for custom application-specific exceptions."""
    logger.warning("Application Exception: %s (Status: %d)", exc.message, exc.status_code)
    return error_response(message=exc.message, errors=exc.errors, status_code=exc.status_code)


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """Handler for Pydantic validation errors."""
    errors = []
    for error in exc.errors():
        errors.append({
            "field": " -> ".join(map(str, error.get("loc", []))),
            "message": error.get("msg"),
            "type": error.get("type")
        })
    logger.warning("Validation Error: %s", errors)
    return error_response(
        message="One or more validation checks failed.",
        errors=errors,
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY
    )


@app.exception_handler(StarletteHTTPException)
async def http_exception_handler(request: Request, exc: StarletteHTTPException):
    """Handler for standard HTTPExceptions."""
    logger.warning("HTTP Exception: %s (Status: %d)", exc.detail, exc.status_code)
    return error_response(message=exc.detail, status_code=exc.status_code)


@app.exception_handler(Exception)
async def generic_exception_handler(request: Request, exc: Exception):
    """Fallback handler for any unhandled unexpected exceptions."""
    logger.exception("Unhandled Exception: %s", str(exc))
    return error_response(
        message="An unexpected server error occurred.",
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
    )


# --- Root Enpoint ---


@app.get("/", tags=["root"])
async def read_root():
    """Welcome endpoint for root path."""
    return success_response(
        message="OptiCrop AI Backend API is online.",
        data={
            "application": settings.APP_NAME,
            "version": settings.APP_VERSION,
            "environment": settings.ENVIRONMENT
        }
    )
