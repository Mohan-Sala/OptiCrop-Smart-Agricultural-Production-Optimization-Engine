from typing import Any, Dict, List, Optional
from fastapi import status


class AppException(Exception):
    """Base application exception for custom error handling."""
    def __init__(
        self,
        message: str,
        status_code: int = status.HTTP_500_INTERNAL_SERVER_ERROR,
        errors: Optional[List[Any]] = None,
    ):
        self.message = message
        self.status_code = status_code
        self.errors = errors or []
        super().__init__(message)


class NotFoundException(AppException):
    def __init__(self, message: str = "Resource not found", errors: Optional[List[Any]] = None):
        super().__init__(message, status.HTTP_404_NOT_FOUND, errors)


class ValidationException(AppException):
    def __init__(self, message: str = "Validation failed", errors: Optional[List[Any]] = None):
        super().__init__(message, status.HTTP_400_BAD_REQUEST, errors)


class AuthenticationException(AppException):
    def __init__(self, message: str = "Authentication failed", errors: Optional[List[Any]] = None):
        super().__init__(message, status.HTTP_401_UNAUTHORIZED, errors)


class AuthorizationException(AppException):
    def __init__(self, message: str = "Access denied", errors: Optional[List[Any]] = None):
        super().__init__(message, status.HTTP_403_FORBIDDEN, errors)


class ConflictException(AppException):
    def __init__(self, message: str = "Resource conflict occurred", errors: Optional[List[Any]] = None):
        super().__init__(message, status.HTTP_409_CONFLICT, errors)
