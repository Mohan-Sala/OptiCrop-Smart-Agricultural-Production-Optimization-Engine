import time
import logging
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from app.core.config import settings

logger = logging.getLogger("app.middleware")


def register_middlewares(app: FastAPI) -> None:
    # 1. CORS Middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.BACKEND_CORS_ORIGINS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # 2. Trusted Host Middleware
    # Restrict hosts in production to prevent HTTP Host Header attacks
    if settings.ENVIRONMENT == "production":
        app.add_middleware(
            TrustedHostMiddleware,
            allowed_hosts=[settings.HOST, "localhost", "127.0.0.1"],
        )

    # 3. Gzip Compression Middleware
    app.add_middleware(GZipMiddleware, minimum_size=1000)

    # 4. Request Logging & Timing Middleware
    @app.middleware("http")
    async def log_request_and_timing(request: Request, call_next):
        start_time = time.time()

        path = request.url.path
        query = request.url.query
        full_path = f"{path}?{query}" if query else path

        client_host = request.client.host if request.client else "unknown"
        logger.info("Incoming Request: %s %s - Client: %s", request.method, full_path, client_host)

        try:
            response = await call_next(request)
            process_time = time.time() - start_time
            ms = process_time * 1000
            response.headers["X-Response-Time"] = f"{ms:.2f}ms"

            logger.info(
                "Request Completed: %s %s - Status: %s - Process Time: %.2fms",
                request.method,
                path,
                response.status_code,
                ms,
            )
            return response
        except Exception as e:
            process_time = time.time() - start_time
            logger.exception(
                "Request Failed: %s %s - Error: %s - Process Time: %.2fms",
                request.method,
                path,
                str(e),
                process_time * 1000,
            )
            raise e
