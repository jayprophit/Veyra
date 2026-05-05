"""
Enterprise Error Handling Middleware
===================================
Centralized error handling with proper logging and response formatting.
Follows industry standards from Stripe, Plaid, and AWS APIs.
"""

import logging
import traceback
from typing import Dict, Any, Optional
from fastapi import Request, Response, HTTPException
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
import structlog

logger = structlog.get_logger(__name__)


class ErrorResponse:
    """Standardized error response format."""
    
    def __init__(
        self,
        error: str,
        message: str,
        status_code: int,
        request_id: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None
    ):
        self.error = error
        self.message = message
        self.status_code = status_code
        self.request_id = request_id
        self.details = details or {}
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON response."""
        response = {
            "error": self.error,
            "message": self.message,
            "status_code": self.status_code
        }
        if self.request_id:
            response["request_id"] = self.request_id
        if self.details:
            response["details"] = self.details
        return response


class ErrorHandlerMiddleware(BaseHTTPMiddleware):
    """Enterprise-grade error handling middleware."""
    
    async def dispatch(self, request: Request, call_next):
        """Process request and handle any errors."""
        request_id = request.headers.get("X-Request-ID", "unknown")
        
        try:
            response = await call_next(request)
            return response
        except HTTPException as e:
            return await self._handle_http_exception(e, request_id)
        except ValueError as e:
            return await self._handle_validation_error(e, request_id)
        except Exception as e:
            return await self._handle_unexpected_error(e, request, request_id)
    
    async def _handle_http_exception(
        self, 
        exc: HTTPException, 
        request_id: str
    ) -> JSONResponse:
        """Handle HTTP exceptions with proper logging."""
        error_response = ErrorResponse(
            error="HTTP_ERROR",
            message=exc.detail,
            status_code=exc.status_code,
            request_id=request_id
        )
        
        logger.warning(
            "HTTP exception occurred",
            status_code=exc.status_code,
            message=exc.detail,
            request_id=request_id
        )
        
        return JSONResponse(
            status_code=exc.status_code,
            content=error_response.to_dict()
        )
    
    async def _handle_validation_error(
        self, 
        exc: ValueError, 
        request_id: str
    ) -> JSONResponse:
        """Handle validation errors."""
        error_response = ErrorResponse(
            error="VALIDATION_ERROR",
            message=str(exc),
            status_code=422,
            request_id=request_id
        )
        
        logger.warning(
            "Validation error occurred",
            error=str(exc),
            request_id=request_id
        )
        
        return JSONResponse(
            status_code=422,
            content=error_response.to_dict()
        )
    
    async def _handle_unexpected_error(
        self, 
        exc: Exception, 
        request: Request, 
        request_id: str
    ) -> JSONResponse:
        """Handle unexpected errors with detailed logging."""
        error_response = ErrorResponse(
            error="INTERNAL_SERVER_ERROR",
            message="An unexpected error occurred. Please try again later.",
            status_code=500,
            request_id=request_id
        )
        
        # Log full error details for debugging
        logger.error(
            "Unexpected error occurred",
            error_type=type(exc).__name__,
            error_message=str(exc),
            traceback=traceback.format_exc(),
            request_id=request_id,
            path=request.url.path,
            method=request.method
        )
        
        return JSONResponse(
            status_code=500,
            content=error_response.to_dict()
        )


class ValidationMiddleware(BaseHTTPMiddleware):
    """Request validation middleware."""
    
    async def dispatch(self, request: Request, call_next):
        """Validate request before processing."""
        # Add request ID if not present
        if not request.headers.get("X-Request-ID"):
            import uuid
            request.state.request_id = str(uuid.uuid4())
        
        # Log request
        logger.info(
            "Incoming request",
            method=request.method,
            path=request.url.path,
            client_ip=request.client.host if request.client else None
        )
        
        response = await call_next(request)
        
        # Log response
        logger.info(
            "Request completed",
            status_code=response.status_code,
            method=request.method,
            path=request.url.path
        )
        
        return response
