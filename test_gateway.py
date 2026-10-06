#!/usr/bin/env python3
"""Tests voor API Gateway."""
import json
import os
import threading
import time
import unittest
import urllib.request
import urllib.error
from http.server import HTTPServer

# Set test API key before importing gateway
os.environ['API_KEY'] = 'test-key-12345'

from gateway import GatewayHandler


class TestGateway(unittest.TestCase):
    """Test suite voor de API Gateway."""

    @classmethod
    def setUpClass(cls):
        """Start een test server op een willekeurige poort."""
        cls.server = HTTPServer(('127.0.0.1', 0), GatewayHandler)
        cls.port = cls.server.server_address[1]
        cls.base_url = f'http://127.0.0.1:{cls.port}'
        cls.server_thread = threading.Thread(target=cls.server.serve_forever, daemon=True)
        cls.server_thread.start()
        time.sleep(0.1)  # Geb de server tijd om op te starten

    @classmethod
    def tearDownClass(cls):
        """Stop de test server."""
        cls.server.shutdown()
        cls.server.server_close()

    def setUp(self):
        """Reset rate limit store before each test."""
        from gateway import rate_limit_store
        rate_limit_store.clear()

    def _get(self, path, headers=None):
        """Helper om een GET request te doen."""
        req = urllib.request.Request(f'{self.base_url}{path}', headers=headers or {})
        try:
            with urllib.request.urlopen(req, timeout=5) as resp:
                return resp.status, json.loads(resp.read().decode())
        except urllib.error.HTTPError as e:
            body = e.read().decode()
            try:
                return e.code, json.loads(body)
            except json.JSONDecodeError:
                return e.code, body

    def test_health_endpoint(self):
        """Test dat /health een 200 OK teruggeeft met status=ok."""
        status, body = self._get('/health')
        self.assertEqual(status, 200)
        self.assertEqual(body['status'], 'ok')
        self.assertIn('uptime', body)
        self.assertIn('version', body)

    def test_unknown_path_returns_401_without_auth(self):
        """Test dat onbekende paden zonder auth een 401 teruggeven."""
        status, _ = self._get('/nonexistent')
        self.assertEqual(status, 401)

    def test_root_path_returns_401_without_auth(self):
        """Test dat / zonder auth een 401 teruggeeft."""
        status, _ = self._get('/')
        self.assertEqual(status, 401)

    def test_unknown_path_with_auth_returns_404(self):
        """Test dat onbekende paden met auth een 404 teruggeven."""
        status, _ = self._get('/nonexistent', headers={'Authorization': 'Bearer test-key-12345'})
        self.assertEqual(status, 404)

    def test_health_content_type(self):
        """Test dat /health de juiste Content-Type header heeft."""
        req = urllib.request.Request(f'{self.base_url}/health')
        with urllib.request.urlopen(req, timeout=5) as resp:
            self.assertEqual(resp.headers.get('Content-Type'), 'application/json')

    def test_server_header(self):
        """Test dat de server een Server header heeft."""
        req = urllib.request.Request(f'{self.base_url}/health')
        with urllib.request.urlopen(req, timeout=5) as resp:
            # BaseHTTPRequestHandler voegt altijd een Server header toe
            self.assertIn('Server', resp.headers)

    def test_metrics_endpoint(self):
        """Test dat /metrics een 200 OK teruggeeft met metrics."""
        status, body = self._get('/metrics')
        self.assertEqual(status, 200)
        self.assertIn('requests_total', body)
        self.assertIn('requests_by_endpoint', body)
        self.assertIn('requests_by_status', body)
        self.assertIn('uptime', body)

    def test_unauthorized_request(self):
        """Test dat verzoeken zonder API key een 401 teruggeven."""
        status, body = self._get('/api/v1/status')
        self.assertEqual(status, 401)
        self.assertEqual(body['error'], 'Unauthorized')

    def test_authorized_request(self):
        """Test dat verzoeken met API key een 200 teruggeven."""
        status, body = self._get('/api/v1/status', headers={'Authorization': 'Bearer test-key-12345'})
        self.assertEqual(status, 200)
        self.assertIn('status', body)
        self.assertIn('services', body)

    def test_services_endpoint(self):
        """Test dat /api/v1/services een lijst van services teruggeeft."""
        status, body = self._get('/api/v1/services', headers={'Authorization': 'Bearer test-key-12345'})
        self.assertEqual(status, 200)
        self.assertIn('services', body)
        self.assertIsInstance(body['services'], list)

    def test_rate_limiting(self):
        """Test dat rate limiting werkt."""
        # Reset rate limit store
        from gateway import rate_limit_store
        rate_limit_store.clear()
        
        # Make requests up to the limit
        for _ in range(100):
            self._get('/health')
        
        # Next request should be rate limited
        status, body = self._get('/health')
        self.assertEqual(status, 429)
        self.assertEqual(body['error'], 'Rate limit exceeded')


if __name__ == '__main__':
    unittest.main()
