from http.server import BaseHTTPRequestHandler
from urllib.parse import parse_qs
import html

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
        if self.path == "/":
            with open("index.html", "r", encoding="utf-8") as f:
                page = f.read()

            # IMPORTANT: echapper les SSID (securite)
            safe_ssids = [html.escape(s) for s in self.available_ssids]

            options_html = build_ssid_options(safe_ssids)

            page = page.replace("{{SSID_OPTIONS}}", options_html)

            self.send_response(200)
            self.send_header("Content-type", "text/html")
            self.end_headers()
            self.wfile.write(page.encode("utf-8"))

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
            self.send_response(302)
            self.send_header("Location", "/")
            self.end_headers()
