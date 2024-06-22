#!/usr/bin/env python3

import sys
import json
import os
import time
from datetime import datetime, timezone
from tzlocal import get_localzone
from watchdog.events import FileSystemEventHandler
from watchdog.observers import Observer

INPUT_PATH = "/input"
CONFIG_FILE = f"{INPUT_PATH}/cosmos.config.json"
CERTS_PATH = "/output/certs"
CERT_FILE = f"{CERTS_PATH}/cert.pem"
KEY_FILE = f"{CERTS_PATH}/key.pem"

curr_valid_until = None

class ConfigFileHandler(FileSystemEventHandler):
    def on_modified(self, event):
        if event.src_path == CONFIG_FILE and os.path.getsize(event.src_path) > 0:
            check_certificate()

def load_config():
    try:
        with open(CONFIG_FILE) as f:
            return json.load(f)
    except Exception:
        return None

def write_certificates(cert, key):
    try:
        with open(CERT_FILE, "w") as cf, open(KEY_FILE, "w") as kf:
            cf.write(cert)
            kf.write(key)
        print("Certificates extracted successfully.")
    except Exception as e:
        print(f"Error writing certificates: {e}")

def check_certificate():
    global curr_valid_until
    config = load_config()
    if not config:
        print("Cosmos config file not found.")
        sys.exit(1)

    cert = config["HTTPConfig"]["TLSCert"]
    key = config["HTTPConfig"]["TLSKey"]
    valid_until = config["HTTPConfig"]["TLSValidUntil"]

    if valid_until == curr_valid_until:
        return

    write_certificates(cert, key)
    curr_valid_until = valid_until

    try:
        valid_until_dt = datetime.strptime(valid_until.split('.', 1)[0] + 'Z', "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=timezone.utc).astimezone(get_localzone())
        print(f"Current date and time: {datetime.now(get_localzone()).strftime('%a %b %d %H:%M:%S %Z %Y')}")
        print(f"Certificate valid until: {valid_until_dt.strftime('%a %b %d %H:%M:%S %Z %Y')}")
    except ValueError:
        print(f"Invalid timestamp format: {valid_until}")

def main():
    if not os.path.isdir(INPUT_PATH) or not os.path.isdir(CERTS_PATH):
        print("Required folder(s) not found.")
        sys.exit(1)

    check_certificate()

    observer = Observer()
    observer.schedule(ConfigFileHandler(), INPUT_PATH, recursive=False)
    observer.start()
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()

if __name__ == "__main__":
    main()
