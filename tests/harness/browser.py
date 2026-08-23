"""Serveur HTTP local + chemins du dépôt.

L'app est servie (et non ouverte en file://) pour disposer d'une vraie origine
(IndexedDB, fetch des exemples) et rester déterministe. Le serveur est enraciné au
dépôt : l'app peut donc résoudre ses chemins relatifs (examples/, etc.).
"""
import functools
import http.server
import socketserver
import threading
from pathlib import Path

# tests/harness/browser.py -> racine du dépôt
ROOT = Path(__file__).resolve().parents[2]
APP_REL = "app/risk-analysis-editor.html"
FIXTURES = ROOT / "tests" / "fixtures"
ARTIFACTS = ROOT / "tests" / "_artifacts"


class _QuietHandler(http.server.SimpleHTTPRequestHandler):
    def log_message(self, *args):  # silencieux
        pass


def start_server(root: Path = ROOT):
    """Démarre un serveur HTTP silencieux sur un port libre. Renvoie (httpd, base_url)."""
    handler = functools.partial(_QuietHandler, directory=str(root))
    httpd = socketserver.ThreadingTCPServer(("127.0.0.1", 0), handler)
    httpd.daemon_threads = True
    port = httpd.server_address[1]
    threading.Thread(target=httpd.serve_forever, daemon=True).start()
    return httpd, f"http://127.0.0.1:{port}"


def app_url(base_url: str) -> str:
    return f"{base_url}/{APP_REL}"
