#!/usr/bin/env python3
"""API Gateway voor fleet services.

Features:
- Health check endpoint
- Rate limiting (per IP)
- API key authentication
- Request routing
- Request logging
- Metrics endpoint
"""
import http.server
import json
import time
import os
import hashlib
import hmac
from collections import defaultdict
from urllib.parse import urlparse, parse_qs

# Configuration
PORT = int(os.environ.get('PORT', 8080))
API_KEY = os.environ.get('API_KEY', 'dev-key-change-in-production')
RATE_LIMIT_WINDOW = int(os.environ.get('RATE_LIMIT_WINDOW', 60))  # seconds
RATE_LIMIT_MAX = int(os.environ.get('RATE_LIMIT_MAX', 100))  # requests per window

# Rate limiting storage
rate_limit_store = defaultdict(list)

# Metrics
metrics = {
    'requests_total': 0,
    'requests_by_endpoint': defaultdict(int),
    'requests_by_status': defaultdict(int),
    'start_time': time.time()
}


def is_rate_limited(client_ip: str) -> bool:
    """Check if client has exceeded rate limit."""
    now = time.time()
    window_start = now - RATE_LIMIT_WINDOW
    
    # Clean old entries
    rate_limit_store[client_ip] = [
        ts for ts in rate_limit_store[client_ip] if ts > window_start
    ]
    
    # Check limit
    if len(rate_limit_store[client_ip]) >= RATE_LIMIT_MAX:
        return True
    
    # Record request
    rate_limit_store[client_ip].append(now)
    return False


def verify_api_key(headers) -> bool:
    """Verify API key from Authorization header."""
    auth = headers.get('Authorization', '')
    if not auth.startswith('Bearer '):
        return False
    token = auth[7:]
    return hmac.compare_digest(token, API_KEY)


class GatewayHandler(http.server.BaseHTTPRequestHandler):
    """HTTP request handler for the API Gateway."""
    
    def log_message(self, format, *args):
        """Override to use structured logging."""
        metrics['requests_total'] += 1
        metrics['requests_by_endpoint'][self.path] += 1
        print(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] {self.client_address[0]} - {format % args}")
    
    def send_json(self, status: int, data: dict):
        """Send JSON response."""
        self.send_response(status)
        self.send_header('Content-Type', 'application/json')
        self.end_headers()
        self.wfile.write(json.dumps(data).encode())
    
    def do_GET(self):
        """Handle GET requests."""
        client_ip = self.client_address[0]
        
        # Rate limiting
        if is_rate_limited(client_ip):
            metrics['requests_by_status'][429] += 1
            self.send_json(429, {'error': 'Rate limit exceeded'})
            return
        
        path = urlparse(self.path).path
        
        # Health check (no auth required)
        if path == '/health':
            metrics['requests_by_status'][200] += 1
            self.send_json(200, {
                'status': 'ok',
                'uptime': time.time() - metrics['start_time'],
                'version': '2.0.0'
            })
            return
        
        # Metrics endpoint (no auth required)
        if path == '/metrics':
            metrics['requests_by_status'][200] += 1
            self.send_json(200, {
                'requests_total': metrics['requests_total'],
                'requests_by_endpoint': dict(metrics['requests_by_endpoint']),
                'requests_by_status': dict(metrics['requests_by_status']),
                'uptime': time.time() - metrics['start_time']
            })
            return
        
        # All other endpoints require auth
        if not verify_api_key(self.headers):
            metrics['requests_by_status'][401] += 1
            self.send_json(401, {'error': 'Unauthorized'})
            return
        
        # Route to backend services
        if path == '/api/v1/status':
            metrics['requests_by_status'][200] += 1
            self.send_json(200, {
                'status': 'operational',
                'services': {
                    'fleet-manager': 'healthy',
                    'api-gateway': 'healthy'
                }
            })
        elif path == '/api/v1/services':
            metrics['requests_by_status'][200] += 1
            self.send_json(200, {
                'services': [
                    {'name': 'fleet-manager', 'url': 'http://fleet-manager:8080'},
                    {'name': 'api-gateway', 'url': 'http://api-gateway:8080'}
                ]
            })
        else:
            metrics['requests_by_status'][404] += 1
            self.send_json(404, {'error': 'Not found'})


def main():
    """Start the API Gateway."""
    server = http.server.HTTPServer(('0.0.0.0', PORT), GatewayHandler)
    print(f'API Gateway actief op poort {PORT}')
    print(f'Rate limit: {RATE_LIMIT_MAX} requests per {RATE_LIMIT_WINDOW}s')
    print(f'API key: {API_KEY[:8]}...')
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print('\nGateway gestopt')
        server.server_close()


if __name__ == '__main__':
    main()
