"""
Monitoring and Observability Setup
"""
import logging
from prometheus_client import Counter, Histogram, Gauge

logger = logging.getLogger(__name__)

# Define metrics
request_counter = Counter(
    'http_requests_total',
    'Total HTTP requests',
    ['method', 'endpoint', 'status']
)

request_duration = Histogram(
    'http_request_duration_seconds',
    'HTTP request duration in seconds',
    ['method', 'endpoint']
)

active_connections = Gauge(
    'http_active_connections',
    'Number of active HTTP connections'
)

graphql_query_duration = Histogram(
    'graphql_query_duration_seconds',
    'GraphQL query duration in seconds',
    ['query_name']
)


def setup_monitoring():
    """Setup monitoring and observability"""
    logger.info("Setting up monitoring...")
    
    # Additional monitoring setup would go here
    # - OpenTelemetry tracing
    # - Structured logging
    # - Exception tracking (Sentry)
