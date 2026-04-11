import time
from django.utils.deprecation import MiddlewareMixin

class RequestPerformanceMiddleware(MiddlewareMixin):
    def process_request(self, request):
        """Store the start time when a request enters the middleware."""
        request.start_time = time.perf_counter()

    def process_response(self, request, response):
        """Calculate duration and add it to the response headers."""
        if hasattr(request, 'start_time'):
            duration = time.perf_counter() - request.start_time
            # Format to milliseconds for better readability
            response['X-Request-Duration-MS'] = f"{duration * 1000:.2f}"
        
        return response
