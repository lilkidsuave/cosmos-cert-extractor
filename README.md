# cosmos-cert-extractor
This is a python script periodically running whenever the certificate expires, whenever the config file changes, or over a set repeatable timer to extract the TLS certificate from the Cosmos config file. The use case I set this up for is in order to use the certificate in my Adguard Home instance.
## How to use
Make sure your volume mounts are set up correctly:
* The `cosmos` volume or path must be mapped to `/input`.
* The `adguard-config` volume must be mapped to `/output/certs`.

The `cert.pem` and `key.pem` file will be created and updated in `/output/certs` and can then be used in Adguard using these paths:
* `/opt/adguardhome/conf/certs/cert.pem`
* `/opt/adguardhome/conf/certs/key.pem`

## Default Values
* `ENV CHECK_INTERVAL = 0` -> Timer in seconds disabled, put value other than 0 to enable.
* `ENV WATCHDOG_ENABLED = true` -> Watchdog enabled, put false or 0 to disable.
