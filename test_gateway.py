#!/usr/bin/env python3
"""Tests voor API Gateway."""
import json
import threading
import time
import unittest
import urllib.request
import urllib.error
from http.server import HTTPServer

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

    def _get(self, path):
        """Helper om een GET request te doen."""
        try:
            with urllib.request.urlopen(f'{self.base_url}{path}', timeout=5) as resp:
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
        self.assertEqual(body, {'status': 'ok'})

    def test_unknown_path_returns_404(self):
        """Test dat onbekende paden een 404 teruggeven."""
        status, _ = self._get('/nonexistent')
        self.assertEqual(status, 404)

    def test_root_path_returns_404(self):
        """Test dat / een 404 teruggeeft."""
        status, _ = self._get('/')
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


if __name__ == '__main__':
    unittest.main()
