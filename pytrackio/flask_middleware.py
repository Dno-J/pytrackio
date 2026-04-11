import time
from flask import request, g

class FlaskPerformanceTracker:
    def __init__(self, app=None):
        if app is not None:
            self.init_app(app)

    def init_app(self, app):
        app.before_request(self.before_request)
        app.after_request(self.after_request)

    def before_request(self):
        g.start_time = time.perf_counter()

    def after_request(self, response):
        if hasattr(g, 'start_time'):
            duration = time.perf_counter() - g.start_time
            response.headers['X-Request-Duration-MS'] = f"{duration * 1000:.2f}"
        return response
