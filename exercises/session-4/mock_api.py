#!/usr/bin/env python3
"""A tiny in-memory REST API for the capstone. No dependencies, stdlib only.

Endpoints:
  GET    /resources/<name>   -> 200 if exists else 404
  POST   /resources          -> 201 (body: {"name": ...})
  DELETE /resources/<name>   -> 204 if existed else 404

Run:  python mock_api.py   (serves on http://127.0.0.1:8000)
State is in-memory and resets when you restart it.
"""
import json
from http.server import BaseHTTPRequestHandler, HTTPServer

RESOURCES = set()


class Handler(BaseHTTPRequestHandler):
    def _send(self, status, payload=None):
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.end_headers()
        if payload is not None:
            self.wfile.write(json.dumps(payload).encode())

    def do_GET(self):
        if self.path.startswith("/resources/"):
            name = self.path[len("/resources/"):]
            if name in RESOURCES:
                self._send(200, {"name": name})
            else:
                self._send(404, {"error": "not found"})
        else:
            self._send(404, {"error": "unknown path"})

    def do_POST(self):
        length = int(self.headers.get("Content-Length", 0))
        body = self.rfile.read(length) if length else b"{}"
        try:
            data = json.loads(body or b"{}")
        except json.JSONDecodeError:
            return self._send(400, {"error": "bad json"})
        name = data.get("name")
        if not name:
            return self._send(400, {"error": "name required"})
        RESOURCES.add(name)
        self._send(201, {"name": name})

    def do_DELETE(self):
        if self.path.startswith("/resources/"):
            name = self.path[len("/resources/"):]
            if name in RESOURCES:
                RESOURCES.discard(name)
                self._send(204)
            else:
                self._send(404, {"error": "not found"})
        else:
            self._send(404, {"error": "unknown path"})

    def log_message(self, *args):
        pass  # quiet


if __name__ == "__main__":
    print("Mock API on http://127.0.0.1:8000  (Ctrl-C to stop)")
    HTTPServer(("127.0.0.1", 8000), Handler).serve_forever()
