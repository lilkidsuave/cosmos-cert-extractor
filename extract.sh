#!/bin/bash
CONFIG_FILE="/var/lib/cosmos/cosmos.config.json"
TLS_CERT_FILE="./tls_cert.pem"
TLS_KEY_FILE="./tls_key.pem"
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
# Function to print current time in Alpine Linux format
function print_current_time {
    date +"%a %b %d %H:%M:%S %Z %Y"
}
# Function to print certificate expiry date
function print_certificate_expiry {
    local expiry_date=$(date -d "$(get_tls_valid_until)" +"%a %b %d %H:%M:%S %Z %Y" 2>/dev/null)
    echo "Certificate valid until: $expiry_date"
}
# Initial certificate setup
update_certificates
CURRENT_VALID_UNTIL=$(get_tls_valid_until)
# Print initial current time and certificate expiry date
echo "Current time: $(print_current_time)"
print_certificate_expiry
# Monitor changes to config file
while true; do
    if inotifywait -q -e modify "$CONFIG_FILE"; then
        NEW_VALID_UNTIL=$(get_tls_valid_until)
        if [ "$NEW_VALID_UNTIL" != "$CURRENT_VALID_UNTIL" ]; then
            CURRENT_VALID_UNTIL="$NEW_VALID_UNTIL"
            update_certificates
            echo "Current time: $(print_current_time)"
            print_certificate_expiry
        fi
    fi
done
