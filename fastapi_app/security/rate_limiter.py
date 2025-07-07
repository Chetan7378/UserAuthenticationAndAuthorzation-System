import time
from collections import defaultdict
from exceptions.custom_exceptions import RateLimitExceeded
from fastapi import Request

# In-memory store for demonstration. Use Redis/Memcached for production.
_REQUEST_COUNTS = defaultdict(lambda: {'count': 0, 'last_reset': time.time()})
RATE_LIMIT_SECONDS = 60  # 1 minute
MAX_REQUESTS_PER_MINUTE = 5 # Example limit

async def rate_limit_dependency(request: Request):
    """FastAPI dependency for rate limiting by client IP."""
    client_ip = request.client.host
    current_time = time.time()

    user_data = _REQUEST_COUNTS[client_ip]

    # Reset count if the time window has passed
    if current_time - user_data['last_reset'] > RATE_LIMIT_SECONDS:
        user_data['count'] = 0
        user_data['last_reset'] = current_time

    user_data['count'] += 1

    if user_data['count'] > MAX_REQUESTS_PER_MINUTE:
        raise RateLimitExceeded()