#!/usr/bin/env python3

from datetime import datetime, timezone
import json
import os
import pytz
import sys
import time
from tzlocal import get_localzone
from watchdog.events import FileSystemEventHandler
from watchdog.observers import Observer

INPUT_PATH = "/input/cosmos.config.json"
CERTS_PATH = "/output/certs"

curr_valid_until = None

class ConfigFileHandler(FileSystemEventHandler):
    def on_modified(self, event):
        if event.src_path == INPUT_PATH and os.path.getsize(event.src_path) > 0:
            check_certificate()

def get_local_timezone():
    # Get the system's local timezone from environment variable or tzlocal
    tz_name = os.getenv('TZ', get_localzone().zone)
    if tz_name:
        try:
            os.system(f'ln -fs /usr/share/zoneinfo/{tz_name} /etc/localtime && \
dpkg-reconfigure -f noninteractive tzdata && \
echo {tz_name} > /etc/timezone')
            with open('/etc/timezone', 'w') as f:
                f.write(tz_name + '\n')
            return pytz.timezone(tz_name)
        except pytz.UnknownTimeZoneError:
            print(f'Invalid timezone specified: {tz_name}. Using UTC instead.')
            return pytz.UTC
    else:
        return get_localzone()

def check_certificate():
    global curr_valid_until
    config_object = load_config()
    if config_object:
        cert = config_object["HTTPConfig"]["TLSCert"]
        key = config_object["HTTPConfig"]["TLSKey"]
        valid_until = config_object["HTTPConfig"]["TLSValidUntil"]
        if valid_until != curr_valid_until:
            write_certificates(cert, key)
            curr_valid_until = valid_until

            # Print certificate expiration date with timezone
            local_tz = get_local_timezone()
            valid_until_dt = datetime.strptime(valid_until, "%Y-%m-%dT%H:%M:%SZ")
            valid_until_dt = valid_until_dt.replace(tzinfo=timezone.utc).astimezone(local_tz)
            print(f"Certificate valid until: {valid_until_dt.strftime('%Y-%m-%d %H:%M:%S %Z%z')}")
    else:
        print("Cosmos config file not found.")
        sys.exit()

def load_config():
    try:
        with open(INPUT_PATH + "/cosmos.config.json", "r") as conf_file:
            return json.load(conf_file)
    except OSError:
        return None

def write_certificates(cert, key):
    with open(CERTS_PATH + "/cert.pem", "w") as cert_file:
        cert_file.write(cert)
    
    with open(CERTS_PATH + "/key.pem", "w") as key_file:
        key_file.write(key)

    print("Cert extracted successfully.")

def main():
    if not os.path.isdir(INPUT_PATH):
        print("Config folder not found.")
        sys.exit()
    if not os.path.isdir(CERTS_PATH):
        print("Certs output folder not found.")
        sys.exit()
    observer = Observer()
    event_handler = ConfigFileHandler()
    observer.schedule(event_handler, INPUT_PATH, recursive=False)
    observer.start()
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()

if __name__ == "__main__":
    main()
