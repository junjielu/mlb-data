#!/usr/bin/env python3
from __future__ import annotations

import argparse
import os
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path


class AppHandler(SimpleHTTPRequestHandler):
    def __init__(self, *args, directory: str | None = None, **kwargs):
        super().__init__(*args, directory=directory, **kwargs)

    def do_GET(self):
        path = self.path.split("?", 1)[0]
        if path in {"/", "/teams"} or path.startswith("/team/"):
            self.path = "/index.html"
        return super().do_GET()


def main() -> int:
    parser = argparse.ArgumentParser(description="Serve frontend with SPA route fallback.")
    parser.add_argument("--root", type=Path, default=Path("public"))
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=4173)
    args = parser.parse_args()

    root = args.root.resolve()
    if not root.exists():
        raise RuntimeError(f"Root not found: {root}")

    os.chdir(root)
    server = ThreadingHTTPServer((args.host, args.port), lambda *a, **kw: AppHandler(*a, directory=str(root), **kw))
    print(f"Serving {root} at http://{args.host}:{args.port}")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
