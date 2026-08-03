from datetime import datetime, timezone
from typing import Any, Generic, List, Optional, TypeVar
from pydantic import BaseModel, Field

T = TypeVar("T")


class BaseResponse(BaseModel, Generic[T]):
    success: bool = Field(..., description="Indicates if the action was executed successfully")
    message: str = Field(..., description="Message describing the outcome")
    data: Optional[T] = Field(None, description="Response payload")
    errors: Optional[List[Any]] = Field(None, description="List of errors if request failed")
    timestamp: str = Field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat(),
        description="ISO timestamp of the response dispatch"
    )
