#!/usr/bin/env python3
"""API Gateway voor fleet services."""
import http.server
import json

class GatewayHandler(http.server.BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/health':
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({'status': 'ok'}).encode())
        else:
            self.send_response(404)
            self.end_headers()

if __name__ == '__main__':
    server = http.server.HTTPServer(('0.0.0.0', 8080), GatewayHandler)
    print('API Gateway actief op poort 8080')
    server.serve_forever()
