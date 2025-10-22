from __future__ import annotations

from typing import Any, Dict, Generic, Optional, TypeVar

from pydantic import BaseModel
from pydantic.generics import GenericModel

T = TypeVar("T")


class ApiResponse(GenericModel, Generic[T]):
    success: bool = True
    message: Optional[str] = None
    data: Optional[T] = None
    meta: Optional[Dict[str, Any]] = None


class ErrorResponse(BaseModel):
    success: bool = False
    message: str
