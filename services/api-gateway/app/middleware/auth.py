"""
Authentication Middleware
"""
from fastapi import Request, HTTPException
from typing import Optional
import logging

logger = logging.getLogger(__name__)


class AuthMiddleware:
    """JWT Authentication Middleware"""
    
    PUBLIC_PATHS = [
        "/health",
        "/docs",
        "/redoc",
        "/openapi.json",
        "/graphql",
    ]
    
    async def process_request(self, request: Request) -> Request:
        """Process and validate authentication"""
        # Skip auth for public paths
        if request.url.path in self.PUBLIC_PATHS:
            return request
        
        # Skip auth for playground (GET to /graphql)
        if request.url.path == "/graphql" and request.method == "GET":
            return request
        
        # Extract token from Authorization header
        auth_header = request.headers.get("Authorization")
        
        if not auth_header:
            # Try to get token from query param (for testing)
            token = request.query_params.get("token")
            if token:
                auth_header = f"Bearer {token}"
        
        if not auth_header or not auth_header.startswith("Bearer "):
            # Allow request but mark as unauthenticated
            request.state.user = None
            request.state.tenant_id = None
            return request
        
        try:
            # Extract and validate token
            token = auth_header.replace("Bearer ", "")
            
            # Decode and validate JWT (implementation would use actual JWT library)
            payload = await self._decode_token(token)
            
            # Add user info to request state
            request.state.user = payload.get("sub")
            request.state.tenant_id = payload.get("tenant_id")
            request.state.roles = payload.get("roles", [])
            
        except Exception as e:
            logger.warning(f"Token validation failed: {e}")
            request.state.user = None
            request.state.tenant_id = None
        
        return request
    
    async def _decode_token(self, token: str) -> dict:
        """Decode and validate JWT token"""
        # This would use python-jose to decode the token
        # For now, return a mock payload
        return {
            "sub": "user-123",
            "tenant_id": "tenant-1",
            "roles": ["admin"],
            "exp": 9999999999,
        }
