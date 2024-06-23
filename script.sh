#!/bin/bash

CONFIG_FILE="/input/cosmos.config.json"
TLS_CERT_FILE="/output/certs/cert.pem"
TLS_KEY_FILE="/output/certs/key.pem"
CURRENT_VALID_UNTIL=""

# Function to update TLS certificates
function update_certificates {
    jq -r '.HTTPConfig.TLSCert' "$CONFIG_FILE" > "$TLS_CERT_FILE"
    jq -r '.HTTPConfig.TLSKey' "$CONFIG_FILE" > "$TLS_KEY_FILE"
    echo "TLSCert has been updated in $TLS_CERT_FILE"
    echo "TLSKey has been updated in $TLS_KEY_FILE"
}

# Function to get TLSValidUntil from config
function get_tls_valid_until {
    jq -r '.HTTPConfig.TLSValidUntil' "$CONFIG_FILE"
}
# Initial certificate setup
update_certificates
CURRENT_VALID_UNTIL=$(get_tls_valid_until)
# Monitor changes to config file
while true; do
    if inotifywait -q -e modify "$CONFIG_FILE"; then
        NEW_VALID_UNTIL=$(get_tls_valid_until)
        if [ "$NEW_VALID_UNTIL" != "$CURRENT_VALID_UNTIL" ]; then
            CURRENT_VALID_UNTIL="$NEW_VALID_UNTIL"
            update_certificates
        fi
    fi
done
