#!/usr/bin/env python3

import json
import os
import signal
import time
from datetime import datetime, timezone
from OpenSSL import crypto
CONFIG_PATH = "/input/cosmos.config.json"
CERT_PATH = "/output/certs/cert.pem"
KEY_PATH = "/output/certs/key.pem"
DEFAULT_CHECK_INTERVAL = 0  # Default check interval is when ot expires

# Event to indicate interruption by signal
interrupted = False

def load_config():
    try:
        with open(CONFIG_PATH, "r") as conf_file:
            return json.load(conf_file)
    except OSError as e:
        print(f"Error reading config file: {e}")
        return None

def load_certificates():
    try:
        with open(CERT_PATH, "r") as cert_file:
            cert_data = cert_file.read()
        with open(KEY_PATH, "r") as key_file:
            key_data = key_file.read()
        return cert_data, key_data
    except OSError as e:
        print(f"Error reading certificates: {e}")
        return None, None

def write_certificates(cert, key):
    try:
        with open(CERT_PATH, "w") as cert_file:
            cert_file.write(cert)
        with open(KEY_PATH, "w") as key_file:
            key_file.write(key)
        print(f"Certificates written successfully.")
    except OSError as e:
        print(f"Error writing certificates: {e}")
        
def renew_certificates():
    global interrupted
    signal.signal(signal.SIGINT, signal_handler)  # Register SIGINT handler
    cert_data, key_data = load_certificates()
    if not cert_data or not key_data:
        print("Couldn't read the certificate or key file.")
    else:
        if is_cert_expired(cert_data) or interrupted:
            print("Certificate expired or interrupted. Updating certificates...")
            config_object = load_config()
            if config_object:
                cert = config_object["HTTPConfig"]["TLSCert"]
                key = config_object["HTTPConfig"]["TLSKey"]
                write_certificates(cert, key)
                interrupted = False  # Reset interruption flag
            else:
                print("Couldn't read the config file.")
            
def is_cert_expired(cert_data):
    cert = crypto.load_certificate(crypto.FILETYPE_PEM, cert_data)
    expiry_date_str = cert.get_notAfter().decode('ascii')
    expiry_date = datetime.strptime(expiry_date_str, '%Y%m%d%H%M%SZ').replace(tzinfo=timezone.utc)
    return expiry_date < datetime.now(timezone.utc)


def get_check_interval():
    try:
        return int(os.getenv('CHECK_INTERVAL', DEFAULT_CHECK_INTERVAL))
    except ValueError:
        print(f"Invalid CHECK_INTERVAL value. Using default: {DEFAULT_CHECK_INTERVAL} seconds.")
        return DEFAULT_CHECK_INTERVAL

def signal_handler(sig, frame):
    global interrupted
    print(f"Received signal {sig}. Updating certificates...")
    interrupted = True
    

def main():
    run_once = False
    next_check_time = time.time()
    
    while True:
        check_interval = get_check_interval()
        current_time = time.time()
        cert_data, key_data = load_certificates()
        
        if not cert_data or not key_data:
            print("Couldn't read the certificate or key file.")
            
        if run_once == False and check_interval > 0:
            renew_certificates()
            print("First Run Certificate")
            print(f"Checking again in {check_interval} seconds.")
            next_check_time = current_time + check_interval
            
        if run_once == False and check_interval == 0:
            renew_certificates()
            print("First Run Certificate")
        # Condition to renew certificates if expired or interrupted
        if is_cert_expired(cert_data) or interrupted and check_interval > 0:
            print("Renewing Certificate")
            renew_certificates()
            print(f"Checking again in {check_interval} seconds.")
            next_check_time = current_time + check_interval  # Update next_check_time
        
        # Print the next check time if not in immediate renewal mode
        if check_interval > 0  and current_time >= next_check_time:
            print("Certificate is still valid.")
            print(f"Checking again in {check_interval} seconds.")
            next_check_time = current_time + check_interval
        
        # Handle the case when CHECK_INTERVAL is 0 and certificate expired or interrupted
        if check_interval == 0 and (is_cert_expired(cert_data) or interrupted):
            print("Renewing Certificate")
            renew_certificates()
            
        run_once = True
        time.sleep(1)


if __name__ == "__main__":
    main()
