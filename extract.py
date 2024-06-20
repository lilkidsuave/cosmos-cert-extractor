#!/usr/bin/env python3

import json
import os
import signal
import threading
import time
from datetime import datetime, timezone
from OpenSSL import crypto
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import pytz
import hashlib
from tzlocal import get_localzone  # Importing get_localzone from tzlocal

# Paths to configuration and certificate files
CONFIG_PATH = '/input/cosmos.config.json'
CERT_PATH = '/output/certs/cert.pem'
KEY_PATH = '/output/certs/key.pem'
DEFAULT_CHECK_INTERVAL = 0  # Default check interval is when it expires
curr_valid_until = 0
valid_until = 1
# Event to indicate interruption by signal
interrupted = False
lock = threading.Lock()

class ConfigFileHandler(FileSystemEventHandler):
    def on_modified(self, event):
        valid_until = config_object["HTTPConfig"]["TLSValidUntil"]
        if event.src_path == CONFIG_PATH and os.path.getsize(event.src_path) > 0 and valid_until != curr_valid_until:
            renew_certificates()

def get_local_timezone():
    # Get the system's local timezone from environment variable or tzlocal
    tz_name = os.getenv('TZ', get_localzone())
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

def convert_to_timezone(utc_timestamp, timezone_str):
    # Convert UTC timestamp to the specified timezone
    utc_dt = datetime.fromisoformat(utc_timestamp[:-1] + '+00:00')
    target_tz = pytz.timezone(timezone_str)
    local_dt = utc_dt.astimezone(target_tz)
    return local_dt

def load_config():
    # Load the configuration from the specified config file.
    try:
        with open(CONFIG_PATH, 'r') as conf_file:
            return json.load(conf_file)
    except OSError as e:
        print(f'Error reading config file: {e}')
        return None

def load_certificates():
    # Load the current certificates from the specified files.
    try:
        with open(CERT_PATH, 'r') as cert_file:
            cert_data = cert_file.read()
        with open(KEY_PATH, 'r') as key_file:
            key_data = key_file.read()
        return cert_data, key_data
    except OSError as e:
        print(f'Error reading certificates: {e}')
        return None, None

def write_certificates(cert, key):
    # Write the new certificates to the specified files.
    try:
        with open(CERT_PATH, 'w') as cert_file:
            cert_file.write(cert)
        with open(KEY_PATH, 'w') as key_file:
            key_file.write(key)
        print('Certificates written successfully.')
    except OSError as e:
        print(f'Error writing certificates: {e}')

def renew_certificates():
    # Renew the certificates by reading from the config file and writing to the certificate files.
    global interrupted
    global curr_valid_until
    global valid_until
    print('Updating certificates...')
    config_object = load_config()
    if config_object:
        cert = config_object['HTTPConfig']['TLSCert']
        key = config_object['HTTPConfig']['TLSKey']
        valid_until = config_object["HTTPConfig"]["TLSValidUntil"]
        write_certificates(cert, key)
        curr_valid_until = valid_until
    else:
        print('Couldn\'t read the config file.')

def get_check_interval():
    # Get the check interval from the environment variable or use the default.
    try:
        return int(os.getenv('CHECK_INTERVAL', DEFAULT_CHECK_INTERVAL))
    except ValueError:
        print(f'Invalid CHECK_INTERVAL value. Using default: {DEFAULT_CHECK_INTERVAL} seconds.')
        return DEFAULT_CHECK_INTERVAL

def get_watchdog_status():
    # Check if the watchdog is enabled based on the environment variable.
    return os.getenv('WATCHDOG_ENABLED', 'false').lower() in ['true', '1', 'yes']

def signal_handler(sig, frame):
    # Handle interrupt signal by setting the interrupted flag.
    global interrupted
    with lock:
        interrupted = True
    print('Received interrupt signal.')
    renew_certificates()
    interrupted = False
    time.sleep(1)

def main():
    global curr_valid_until
    global valid_until
    signal.signal(signal.SIGINT, signal_handler)  # Register SIGINT handler
    next_check_time = time.time()
    tz = get_local_timezone()  # Get the local timezone
    renew_certificates()  # Initial renewal of certificates
    watchdog_enabled = get_watchdog_status()  # Check if watchdog is enabled
    print(f'New certificate expires on {convert_to_timezone(curr_valid_until, tz)}.')

    if watchdog_enabled:
        print('Watchdog enabled. Monitoring the configuration file for changes.')
        event_handler = ConfigFileHandler()
        observer = Observer()
        observer.schedule(event_handler, path=os.path.dirname(CONFIG_PATH), recursive=False)
        observer.start()

    while True:
        interrupted = False
        check_interval = get_check_interval()  # Get the check interval
        current_time = time.time()
        # Condition to renew certificates if expired or interrupted
        valid_until = config_object["HTTPConfig"]["TLSValidUntil"]
        if valid_until != curr_valid_until and check_interval > 0:
            old_valid_until = curr_valid_until
            renew_certificates()
            print(f'Certificate expired on: {convert_to_timezone(old_valid_until, tz)}. Updating again in {check_interval} seconds.')
            next_check_time = current_time + check_interval  # Update next_check_time
        elif check_interval > 0 and current_time >= next_check_time:
            renew_certificates()
            print(f'Updating again in {check_interval} seconds.')
            next_check_time = current_time + check_interval
        # Handle the case when CHECK_INTERVAL is 0 and certificate expired or interrupted
        elif check_interval == 0 and valid_until != curr_valid_until:
            renew_certificates()
            print(f'Certificate expired on: {convert_to_timezone(old_valid_until, tz)}. New certificate expires on {expiry_date.isoformat()} {expiry_date.tzinfo}.')

        time.sleep(1)

if __name__ == '__main__':
    main()
