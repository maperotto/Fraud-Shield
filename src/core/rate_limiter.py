from flask import request, jsonify
from functools import wraps
import time
from collections import defaultdict
from threading import Lock


class RateLimiter:
    def __init__(self, max_requests: int = 100, window_seconds: int = 60):
        self.max_requests = max_requests
        self.window_seconds = window_seconds
        self.requests = defaultdict(list)
        self.lock = Lock()
    
    def is_allowed(self, key: str) -> bool:
        current_time = time.time()
        
        with self.lock:
            if key not in self.requests:
                self.requests[key] = []
            
            self.requests[key] = [
                req_time for req_time in self.requests[key]
                if current_time - req_time < self.window_seconds
            ]
            
            if len(self.requests[key]) < self.max_requests:
                self.requests[key].append(current_time)
                return True
            
            return False
    
    def get_remaining(self, key: str) -> int:
        current_time = time.time()
        
        with self.lock:
            if key not in self.requests:
                return self.max_requests
            
            recent_requests = [
                req_time for req_time in self.requests[key]
                if current_time - req_time < self.window_seconds
            ]
            
            return max(0, self.max_requests - len(recent_requests))


rate_limiter = RateLimiter(max_requests=100, window_seconds=60)


def rate_limit(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        client_ip = request.remote_addr or 'unknown'
        
        if not rate_limiter.is_allowed(client_ip):
            return jsonify({
                'error': 'Rate limit exceeded',
                'message': 'Too many requests. Please try again later.'
            }), 429
        
        remaining = rate_limiter.get_remaining(client_ip)
        response = func(*args, **kwargs)
        
        if isinstance(response, tuple):
            response_obj, status_code = response
        else:
            response_obj = response
            status_code = 200
        
        if hasattr(response_obj, 'headers'):
            response_obj.headers['X-RateLimit-Remaining'] = str(remaining)
        
        return response_obj, status_code
    
    return wrapper
