from typing import Any, List, Optional
from fastapi.responses import JSONResponse
from app.schemas.response import BaseResponse


def json_response(
    status_code: int,
    success: bool,
    message: str,
    data: Any = None,
    errors: Optional[List[Any]] = None,
) -> JSONResponse:
    """Generates a standardized JSON response based on the BaseResponse schema."""
    response_model = BaseResponse(
        success=success,
        message=message,
        data=data,
        errors=errors,
    )
    # Using model_dump() for standard serialization (Pydantic v2)
    return JSONResponse(status_code=status_code, content=response_model.model_dump())


def success_response(
    message: str = "Action completed successfully",
    data: Any = None,
    status_code: int = 200,
) -> JSONResponse:
    """Helper for returning a successful JSON response."""
    return json_response(status_code=status_code, success=True, message=message, data=data)


def error_response(
    message: str = "An error occurred",
    errors: Optional[List[Any]] = None,
    status_code: int = 400,
) -> JSONResponse:
    """Helper for returning an error JSON response."""
    return json_response(status_code=status_code, success=False, message=message, errors=errors)
