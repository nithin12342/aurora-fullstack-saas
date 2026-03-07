"""
Aurora Fullstack SaaS - Pytest Configuration

This file contains shared fixtures and configuration for all Aurora tests.
"""
import pytest
from unittest.mock import Mock, AsyncMock


@pytest.fixture
def mock_api_gateway():
    """Mock API Gateway service"""
    gateway = Mock()
    gateway.process_request = AsyncMock(return_value={"status": "success"})
    gateway.health_check = AsyncMock(return_value={"status": "healthy"})
    return gateway


@pytest.fixture
def mock_rate_limiter():
    """Mock Rate Limiter middleware"""
    limiter = Mock()
    limiter.check_limit = Mock(return_value=True)
    limiter.get_remaining = Mock(return_value=100)
    return limiter


@pytest.fixture
def sample_user_data():
    """Sample user data for testing"""
    return {
        "id": "user-123",
        "email": "test@example.com",
        "name": "Test User",
        "role": "admin"
    }


@pytest.fixture
def sample_request_data():
    """Sample API request data"""
    return {
        "method": "POST",
        "path": "/api/users",
        "headers": {"Content-Type": "application/json"},
        "body": {"name": "Test User", "email": "test@example.com"}
    }


@pytest.fixture
def auth_token():
    """Mock authentication token"""
    return "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.mock_token"


@pytest.fixture
def rate_limit_config():
    """Rate limiter configuration"""
    return {
        "max_requests": 100,
        "window_seconds": 60,
        "burst_size": 10
    }
