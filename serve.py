#!/usr/bin/env python3
"""
Simple HTTP server to serve frontend files on port 3000
while backend API runs on port 8888
"""

import http.server
import socketserver
import os

PORT = 3000
DIRECTORY = "."

class MyHTTPRequestHandler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=DIRECTORY, **kwargs)
    
    def log_message(self, format, *args):
        print(f"[{self.client_address[0]}] {format % args}")

try:
    with socketserver.TCPServer(("", PORT), MyHTTPRequestHandler) as httpd:
        print(f"""
╔════════════════════════════════════════════════════════════╗
║         Frontend Server Running                            ║
╠════════════════════════════════════════════════════════════╣
║  Frontend (this server): http://127.0.0.1:{PORT}           ║
║  Backend API:            http://127.0.0.1:8888/api         ║
║                                                             ║
║  Open your browser to:                                     ║
║  http://127.0.0.1:{PORT}/index_new.html                   ║
║  http://127.0.0.1:{PORT}/TEST_API.html (for testing)      ║
║                                                             ║
║  Press Ctrl+C to stop the server                           ║
╚════════════════════════════════════════════════════════════╝
""")
        httpd.serve_forever()
except KeyboardInterrupt:
    print("\nServer stopped")
except OSError as e:
    if "Address already in use" in str(e):
        print(f"❌ Error: Port {PORT} is already in use")
        print(f"   Kill the process using: netstat -ano | findstr :{PORT}")
    else:
        print(f"❌ Error: {e}")
