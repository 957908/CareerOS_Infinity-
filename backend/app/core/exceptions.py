from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse
import logging

logger = logging.getLogger("app.core.exceptions")

class BaseAPIException(Exception):
    """
    Standard Base exception for all API routing errors in CareerOS.
    """
    def __init__(self, detail: str, status_code: int = status.HTTP_400_BAD_REQUEST):
        super().__init__(detail)
        self.detail = detail
        self.status_code = status_code

class AuthenticationError(BaseAPIException):
    def __init__(self, detail: str = "Invalid authentication credentials"):
        super().__init__(detail, status_code=status.HTTP_401_UNAUTHORIZED)

class PermissionDenied(BaseAPIException):
    def __init__(self, detail: str = "Permission denied"):
        super().__init__(detail, status_code=status.HTTP_403_FORBIDDEN)

class NotFoundError(BaseAPIException):
    def __init__(self, detail: str = "Requested resource not found"):
        super().__init__(detail, status_code=status.HTTP_404_NOT_FOUND)

class ValidationError(BaseAPIException):
    def __init__(self, detail: str = "Request validation failed"):
        super().__init__(detail, status_code=status.HTTP_422_UNPROCESSABLE_ENTITY)

def register_custom_exception_handlers(app: FastAPI) -> None:
    """
    Binds custom API exceptions to the FastAPI gateway server instance.
    """
    @app.exception_handler(BaseAPIException)
    async def base_api_exception_handler(request: Request, exc: BaseAPIException) -> JSONResponse:
        logger.warning(f"API exception status={exc.status_code} detail={exc.detail}")
        return JSONResponse(
            status_code=exc.status_code,
            content={"detail": exc.detail}
        )
