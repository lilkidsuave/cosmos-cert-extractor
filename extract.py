#!/usr/bin/env python3

import sys, json, os, time
from datetime import datetime, timezone
from tzlocal import get_localzone
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
INPUT_PATH = "/input"
CERTS_PATH = "/output/certs"
curr_valid_until = None
class ConfigFileHandler(FileSystemEventHandler):
    def on_modified(self, event):
        if event.src_path == INPUT_PATH + "/cosmos.config.json" and os.path.getsize(event.src_path) > 0:
            check_certificate()

def load_config():
    try:
        with open(INPUT_PATH + "/cosmos.config.json", "r") as conf_file:
            return json.load(conf_file)
    except Exception as e:
        print(f"Error loading config file: {e}")
        return None

def write_certificates(cert, key):
    try:
        with open(f"{CERTS_PATH}/cert.pem", "w") as cf, open(f"{CERTS_PATH}/key.pem", "w") as kf:
            cf.write(cert)
            kf.write(key)
        print("Certificates extracted successfully.")
    except Exception as e:
        print(f"Error writing certificates: {e}")

def check_certificate():
    global curr_valid_until
    config = load_config()
    if not config:
        sys.exit("Config file not found or invalid.")
    http_config = config.get("HTTPConfig", {})
    cert, key, valid_until = http_config.get("TLSCert"), http_config.get("TLSKey"), http_config.get("TLSValidUntil")
    if valid_until == curr_valid_until:
        return
    write_certificates(cert, key)
    curr_valid_until = valid_until
    try:
        valid_until_dt = datetime.strptime(valid_until.split('.')[0] + 'Z', "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=timezone.utc).astimezone(get_localzone())
        print(f"Current time: {datetime.now(get_localzone()).strftime('%a %b %d %H:%M:%S %Z %Y')}")
        print(f"Certificate valid until: {valid_until_dt.strftime('%a %b %d %H:%M:%S %Z %Y')}")
    except ValueError as e:
        print(f"Error processing timestamp: {e}")

def main():
    if not all(os.path.isdir(path) for path in (INPUT_PATH, CERTS_PATH)):
        sys.exit("Required folder(s) not found.")
    check_certificate()
    observer = Observer(timeout=0.1)
    observer.schedule(ConfigFileHandler(), INPUT_PATH, recursive=False)
    observer.start()
    try:
        while True:
            observer.join(timeout=1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()
if __name__ == "__main__":
    main()
