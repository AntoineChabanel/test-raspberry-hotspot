from http.server import BaseHTTPRequestHandler
from urllib.parse import parse_qs, urlparse, urlencode
import mimetypes
import os
import html

CAPTIVE_PORTAL_DETECTION_PATHS = {
    "/hotspot-detect.html",           # Apple (iOS / macOS)
    "/library/test/success.html",     # Apple (ancien)
    "/generate_204",                  # Android / Chrome
    "/connecttest.txt",               # Windows
    "/redirect",                      # Windows
    "/ncsi.txt",                      # Windows
    "/success.txt",                   # Diverse
}

class SsidAndPassword:
    ssid = None
    password = None

def build_ssid_options(ssids):
    html = ""
    for ssid in ssids:
        html += f'<option value="{ssid}">{ssid}</option>\n'
    return html

class PortalHandler(BaseHTTPRequestHandler):

    available_ssids = []
    ssid_and_password = SsidAndPassword()

    def do_GET(self):
        parsed = urlparse(self.path)
        path_only = parsed.path.rstrip("/") or "/"
        if path_only != "/" and path_only in CAPTIVE_PORTAL_DETECTION_PATHS:
            self.send_response(302)
            self.send_header("Location", "/")
            self.end_headers()
            return
        if self.path == "/" or path_only == "/":
            with open("index.html", "r", encoding="utf-8") as f:
                page = f.read()

            safe_ssids = [html.escape(s) for s in self.available_ssids]

            options_html = build_ssid_options(safe_ssids)

            page = page.replace("{{SSID_OPTIONS}}", options_html)

            self.send_response(200)
            self.send_header("Content-type", "text/html")
            self.end_headers()
            self.wfile.write(page.encode("utf-8"))
        else:
            file_path = parsed.path.lstrip("/")
            if os.path.isfile(file_path):
                mime_type, _ = mimetypes.guess_type(file_path)
                self.send_response(200)
                self.send_header("Content-type", mime_type or "application/octet-stream")
                self.end_headers()
                with open(file_path, "rb") as f:
                    self.wfile.write(f.read())
            else:
                self.send_response(404)
                self.end_headers()

    def do_POST(self):
        if self.path == "/submit":
            content_length = int(self.headers.get("Content-Length", 0))
            body = self.rfile.read(content_length).decode("utf-8")
            params = parse_qs(body)
            ssid = params.get("ssid", [None])[0]
            password = params.get("password", [None])[0]
            print(f"SSID: {ssid}, Password: {password}")
            self.ssid_and_password.ssid = ssid
            self.ssid_and_password.password = password
            success_msg = "Data has been sent. The device will attempt to connect to the network you provided."
            self.send_response(302)
            self.send_header("Location", "/?" + urlencode({"msg": success_msg}))
            self.end_headers()
