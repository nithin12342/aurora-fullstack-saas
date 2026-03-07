"""
Aurora API Gateway - GraphQL API
Main entry point for the GraphQL API Gateway
"""
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import logging
import time

from app.config import settings
from app.graphql import schema
from app.middleware.rate_limiter import RateLimiter
from app.middleware.auth import AuthMiddleware
from app.monitoring import setup_monitoring

logging.basicConfig(level=settings.LOG_LEVEL)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan handler"""
    # Startup
    logger.info("Starting Aurora API Gateway...")
    setup_monitoring()
    
    yield
    
    # Shutdown
    logger.info("Shutting down Aurora API Gateway...")


app = FastAPI(
    title="Aurora API Gateway",
    description="GraphQL API Gateway for Aurora SaaS Platform",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Rate limiting middleware
@app.middleware("http")
async def rate_limit_middleware(request: Request, call_next):
    """Apply rate limiting to all requests"""
    if settings.RATE_LIMIT_ENABLED:
        rate_limiter = RateLimiter(
            requests_per_minute=settings.RATE_LIMIT_PER_MINUTE,
        )
        await rate_limiter.check_rate_limit(request)
    response = await call_next(request)
    return response


# Auth middleware
@app.middleware("http")
async def auth_middleware(request: Request, call_next):
    """Apply authentication to all requests"""
    auth_middleware = AuthMiddleware()
    request = await auth_middleware.process_request(request)
    response = await call_next(request)
    return response


# Request timing middleware
@app.middleware("http")
async def timing_middleware(request: Request, call_next):
    """Add request timing headers"""
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    response.headers["X-Process-Time"] = str(process_time)
    return response


# Error handler
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Handle all unhandled exceptions"""
    logger.error(f"Unhandled exception: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={
            "error": {
                "code": "INTERNAL_SERVER_ERROR",
                "message": "An unexpected error occurred",
            }
        },
    )


# Health check endpoint
@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "service": "api-gateway"}


# GraphQL endpoint
@app.post("/graphql")
async def graphql_endpoint(request: Request):
    """GraphQL endpoint"""
    from strawberry.fastz import create_fiber_view
    
    # Get request body
    body = await request.json()
    query = body.get("query")
    variables = body.get("variables", {})
    operation_name = body.get("operation_name")
    
    # Execute query
    result = await schema.execute(
        query=query,
        variables=variables,
        operation_name=operation_name,
        context_value={"request": request},
    )
    
    # Format response
    if result.errors:
        return {
            "errors": [
                {
                    "message": error.message,
                    "locations": error.locations,
                    "path": error.path,
                }
                for error in result.errors
            ]
        }
    
    return {"data": result.data}


@app.get("/graphql")
async def graphql_playground():
    """GraphQL Playground endpoint"""
    from strawberry.fastz import render_graphql_playground
    
    return render_graphql_playground()


# Metrics endpoint
@app.get("/metrics")
async def metrics():
    """Prometheus metrics endpoint"""
    from prometheus_client import generate_latest, CONTENT_TYPE_LATEST
    
    return generate_latest(), 200, {"Content-Type": CONTENT_TYPE_LATEST}


if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.DEBUG,
        log_level=settings.LOG_LEVEL.lower(),
    )
