import http.server
import socketserver

PORT = 7860

class SwarmHandler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header("Content-type", "application/json")
        self.end_headers()
        self.wfile.write(b'{"status": "online", "role": "OPPO Recon", "vote": "HOLDING_FLOOR"}')
        print("📡 Handshake Sent to Citadel S10+")

with socketserver.TCPServer(("0.0.0.0", PORT), SwarmHandler) as httpd:
    print(f"🐝 OPPO Node Active. Listening for S10+ on port {PORT}...")
    httpd.serve_forever()
