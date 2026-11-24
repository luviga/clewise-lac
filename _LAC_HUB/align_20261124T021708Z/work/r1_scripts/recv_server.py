"""Tiny one-purpose upload receiver on 127.0.0.1 for saving files fetched in the browser pane.
Usage: python -I recv_server.py <out_dir> <port>
POST /<filename> with the raw bytes as body; saved to out_dir/filename (basename only)."""
import os, sys
from http.server import BaseHTTPRequestHandler, HTTPServer

OUT = sys.argv[1]
PORT = int(sys.argv[2])


class H(BaseHTTPRequestHandler):
    def _cors(self):
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "*")
        self.send_header("Access-Control-Allow-Private-Network", "true")

    def do_OPTIONS(self):
        self.send_response(204)
        self._cors()
        self.end_headers()

    def do_POST(self):
        name = os.path.basename(self.path.split("?")[0]) or "upload.bin"
        n = int(self.headers.get("Content-Length", "0"))
        data = self.rfile.read(n)
        with open(os.path.join(OUT, name), "wb") as f:
            f.write(data)
        self.send_response(200)
        self._cors()
        self.end_headers()
        self.wfile.write(f"saved {name} {len(data)}".encode())


HTTPServer(("127.0.0.1", PORT), H).serve_forever()
