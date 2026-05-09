"""
OpenAPI/Swagger Documentation Setup
Auto-generates API documentation from FastAPI routes
"""

from fastapi import FastAPI, APIRouter
from fastapi.openapi.utils import get_openapi
from functools import lru_cache
import json


def setup_openapi(app: FastAPI):
    """Configure OpenAPI/Swagger documentation for Financial Master."""

    def custom_openapi():
        """Generate custom OpenAPI schema."""
        if app.openapi_schema:
            return app.openapi_schema

        openapi_schema = get_openapi(
            title="Financial Master API",
            version="1.0.0",
            description="""
            # Financial Master - Open-Source Bloomberg Terminal Alternative

            ## Features
            - Real-time market data
            - Trading execution
            - Portfolio management
            - Risk analysis
            - Advanced analytics

            ## Authentication
            All endpoints (except `/docs`, `/health`) require Bearer token authentication.

            ```
            Authorization: Bearer <your_token>
            ```

            ## Rate Limiting
            - Public endpoints: 100 requests/minute
            - Authenticated endpoints: 1000 requests/minute

            ## Response Codes
            - 200: Success
            - 400: Bad Request
            - 401: Unauthorized
            - 403: Forbidden
            - 404: Not Found
            - 422: Validation Error
            - 500: Internal Server Error
            """,
            routes=app.routes,
            tags_metadata=[
                {
                    "name": "Trading",
                    "description": "Trade execution and order management",
                    "externalDocs": {
                        "description": "Learn more",
                        "url": "https://financial-master.docs/trading",
                    },
                },
                {
                    "name": "Portfolio",
                    "description": "Portfolio management and tracking",
                    "externalDocs": {
                        "description": "Learn more",
                        "url": "https://financial-master.docs/portfolio",
                    },
                },
                {
                    "name": "Market Data",
                    "description": "Real-time and historical market data",
                    "externalDocs": {
                        "description": "Learn more",
                        "url": "https://financial-master.docs/market-data",
                    },
                },
                {
                    "name": "Analytics",
                    "description": "Advanced analytics and insights",
                    "externalDocs": {
                        "description": "Learn more",
                        "url": "https://financial-master.docs/analytics",
                    },
                },
                {
                    "name": "Risk Management",
                    "description": "Risk analytics and monitoring",
                    "externalDocs": {
                        "description": "Learn more",
                        "url": "https://financial-master.docs/risk",
                    },
                },
            ],
        )

        # Add servers for deployment options
        openapi_schema["servers"] = [
            {
                "url": "https://api.financial-master.com",
                "description": "Production Server",
            },
            {
                "url": "https://staging-api.financial-master.com",
                "description": "Staging Server",
            },
            {
                "url": "http://localhost:8000",
                "description": "Local Development",
            },
        ]

        # Add security schemes
        openapi_schema["components"]["securitySchemes"] = {
            "bearerAuth": {
                "type": "http",
                "scheme": "bearer",
                "bearerFormat": "JWT",
                "description": "JWT Bearer token authentication",
            }
        }

        # Add common response schemas
        openapi_schema["components"]["schemas"]["ErrorResponse"] = {
            "type": "object",
            "properties": {
                "detail": {"type": "string"},
                "status": {"type": "integer"},
                "timestamp": {"type": "string", "format": "date-time"},
            },
            "required": ["detail", "status"],
        }

        openapi_schema["components"]["schemas"]["TradeResponse"] = {
            "type": "object",
            "properties": {
                "trade_id": {"type": "string"},
                "ticker": {"type": "string"},
                "quantity": {"type": "number"},
                "price": {"type": "number"},
                "total": {"type": "number"},
                "status": {"type": "string", "enum": ["pending", "executed", "cancelled"]},
                "timestamp": {"type": "string", "format": "date-time"},
            },
            "required": ["trade_id", "ticker", "quantity", "price"],
        }

        app.openapi_schema = openapi_schema
        return app.openapi_schema

    app.openapi = custom_openapi

    # Configure Swagger UI
    app.swagger_ui_parameters = {
        "displayOperationId": True,
        "docExpansion": "list",
        "defaultModelsExpandDepth": 2,
        "presets": [
            "swaggerUIBundle.presets.apis",
            "swaggerUIBundle.SwaggerUIStandalonePreset",
        ],
    }

    print("✓ OpenAPI/Swagger documentation configured")
    print(f"  Access at: /docs (Swagger UI) or /redoc (ReDoc)")


# Example: How to add this to your main FastAPI app
"""
# In your main_enterprise.py:

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Setup OpenAPI
from api_docs import setup_openapi
setup_openapi(app)

# Your routes here...
@app.get("/trades", tags=["Trading"])
async def get_trades():
    \"\"\"
    Get all trades for the authenticated user.

    Returns:
        List of trades with execution details
    \"\"\"
    pass

# Run with: uvicorn main_enterprise:app --reload
# Access docs at: http://localhost:8000/docs
"""
