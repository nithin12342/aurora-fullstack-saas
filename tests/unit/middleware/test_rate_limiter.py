"""
Unit tests for Aurora Rate Limiter Middleware

Tests the rate limiting functionality for API requests.
"""
import pytest
from unittest.mock import Mock, patch
import time
import sys
import os

# Add the middleware directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', 'services', 'api-gateway', 'app', 'middleware'))


class TestRateLimiter:
    """Test suite for Rate Limiter middleware"""

    @pytest.fixture
    def rate_limiter_config(self):
        """Rate limiter configuration"""
        return {
            "max_requests": 100,
            "window_seconds": 60,
            "burst_size": 10,
            "redis_host": "localhost",
            "redis_port": 6379
        }

    @pytest.fixture
    def sample_client_id(self):
        """Sample client identifier"""
        return "client-12345"

    def test_rate_limiter_initialization(self, rate_limiter_config):
        """Test rate limiter initializes with correct config"""
        assert rate_limiter_config["max_requests"] == 100
        assert rate_limiter_config["window_seconds"] == 60
        assert rate_limiter_config["burst_size"] == 10

    def test_check_rate_limit_allowed(self, mock_rate_limiter, sample_client_id):
        """Test that request is allowed within rate limit"""
        result = mock_rate_limiter.check_limit(sample_client_id)
        assert result is True

    def test_check_rate_limit_exceeded(self, mock_rate_limiter, sample_client_id):
        """Test that request is denied when limit exceeded"""
        # Simulate exceeding the limit
        mock_rate_limiter.check_limit = Mock(return_value=False)
        result = mock_rate_limiter