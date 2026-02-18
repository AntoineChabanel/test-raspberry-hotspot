import subprocess
from http.server import ThreadingHTTPServer
from webserver.portal_handler import PortalHandler
from concurrent.futures import ThreadPoolExecutor
import atexit
import signal
import sys
import os
from dotenv import load_dotenv

httpd = None

class SsidWebserver:
    def __init__(self, available_networks):
        self.available_networks = available_networks
        os.chdir("portal")
        PortalHandler.available_ssids = self.available_networks
        self.httpd = ThreadingHTTPServer(("0.0.0.0", 80), PortalHandler)

    def handle_request_thread(self):
        while PortalHandler.ssid_and_password.ssid is None or PortalHandler.ssid_and_password.ssid is '':
            self.httpd.handle_request()
        print(f"SSID: {PortalHandler.ssid_and_password.ssid}, Password: {PortalHandler.ssid_and_password.password}")
        return PortalHandler.ssid_and_password

def extractUniqueSsids(output):
    lines = output.strip().split('\n')
    ssid_list = {line.strip() for line in lines[1:] if line.strip() != '--'}
    return list(ssid_list)

def scan_networks():
    try:
        return extractUniqueSsids(subprocess.run(['nmcli', '-f', 'SSID', 'device', 'wifi'], capture_output=True, text=True).stdout)
    except Exception as e:
        print(f"Error scanning networks: {e}")
        raise Exception(f"Error scanning networks: {e}")

def create_hotspot():
    try:
        subprocess.run(['sudo', 'nmcli', 'dev', 'wifi', 'hotspot', 'ifname', 'wlan0', 'ssid', 'BrEye-Setup', 'password', 'setup-1234'])
        print("Hotspot created successfully")
    except Exception as e:
        print(f"Error creating hotspot: {e}")
        raise Exception(f"Error creating hotspot: {e}")

def remove_hotspot():
    try:
        subprocess.run(['sudo', 'nmcli', 'dev', 'wifi', 'hotspot', 'ifname', 'wlan0', 'remove'])
        print("Hotspot removed successfully")
    except Exception as e:
        print(f"Error removing hotspot: {e}")
        raise Exception(f"Error removing hotspot: {e}")



def __main__():
    load_dotenv()
    atexit.register(remove_hotspot)
    signal.signal(signal.SIGTERM, lambda sig, frame: sys.exit(0))
    dummy_wifi = os.getenv("DUMMY_WIFI")
    if dummy_wifi:
        dummy_wifi = dummy_wifi.lower() == "true"
    else:
        dummy_wifi = False

    try:
        requests.head('https://www.google.com/', timeout=1).status_code
        wifi_ok = True
        print("Wifi connected successfully or was already connected")
    except:
        pass

    available_networks = []
    if not dummy_wifi:
        try:
            available_networks = scan_networks()
        except Exception as e:
            print(f"Error scanning networks: {e}")
            return
    else:
        available_networks = ["wifidemelchior","wifidepaul","wifidetheo","wifideamalia","wifidejulian","wifidejean","wifideantoine"]

    print("Available networks:")
    for network in available_networks:
        print(network)
    
    try:
        create_hotspot()
    except Exception as e:
        print(f"Error creating hotspot: {e}")
        remove_hotspot()
        return


    try:
        ssid_webserver = SsidWebserver(available_networks)
        with ThreadPoolExecutor() as executor:
            future = executor.submit(ssid_webserver.handle_request_thread)
            ssid_and_password = future.result()  # like std::future
            print(f"Connexion au WiFi : {ssid_and_password.ssid}")
    except Exception as e:
        print(f"Error during webserver: {e}")

    # connect to the wifi
    if not dummy_wifi:
        try:
            subprocess.run(['sudo', 'nmcli', 'dev', 'wifi', 'connect', ssid_and_password.ssid, 'password', ssid_and_password.password])
            print("Connected to the WiFi")
        except Exception as e:
            print(f"Error connecting to the WiFi: {e}")

    remove_hotspot()


if __name__ == "__main__":
    __main__()