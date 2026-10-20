"""Local dev server for the Time Debt Clock PWA.

Service workers only register on http:// (not file://), so use this to test:

    python serve.py          # http://127.0.0.1:8080
    python serve.py 9000     # custom port

Serves this folder with the manifest's correct MIME type and no-cache headers.
"""
import functools
import http.server
import mimetypes
import socketserver
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
PORT = int(sys.argv[1]) if len(sys.argv) > 1 else 8080

mimetypes.add_type("application/manifest+json", ".webmanifest")
mimetypes.add_type("image/svg+xml", ".svg")


class Handler(http.server.SimpleHTTPRequestHandler):
    def end_headers(self):
        # Dev convenience: browsers must not cache the shell/SW while iterating.
        self.send_header("Cache-Control", "no-cache")
        super().end_headers()


def main() -> None:
    handler = functools.partial(Handler, directory=str(ROOT))
    socketserver.ThreadingTCPServer.allow_reuse_address = True
    with socketserver.ThreadingTCPServer(("127.0.0.1", PORT), handler) as httpd:
        print(f"Serving {ROOT} at http://127.0.0.1:{PORT}/  (Ctrl+C to stop)")
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("stopped")


if __name__ == "__main__":
    main()
