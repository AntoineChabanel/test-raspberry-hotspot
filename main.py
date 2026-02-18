import subprocess

def extractUniqueSsids(output):
    lines = output.strip().split('\n')
    ssid_list = {line.strip() for line in lines[1:] if line.strip() != '--'}
    return list(ssid_list)

def scan_networks():
    try:
        return extractUniqueSsids(subprocess.run(['nmcli', '-f', 'SSID', 'device', 'wifi'], capture_output=True, text=True).stdout)
    except Exception as e:
        print(f"Error scanning networks: {e}")
        return ["wifi","error"]

def __main__():
    print(scan_networks())

if __name__ == "__main__":
    __main__()