# cosmos-cert-extractor
This is a python script monitoring your [Cosmos](https://github.com/azukaar/Cosmos-Server) config file for changes in order to extract the TLS certificate from it. My personal use case is to re-use the certificate in my Adguard Home instance.
## How to use
This branch uses python3.12-slim which is Debian Slim with Python.
Make sure your volume mounts are set up correctly:
* The `cosmos` volume or path must be mapped to `/input`.
* The `adguard-config` volume must be mapped to `/output/certs`.
The `cert.pem` and `key.pem` file will be created and updated in `/output/certs` and can then be used in Adguard using these paths:
* `/opt/adguardhome/conf/certs/cert.pem`
* `/opt/adguardhome/conf/certs/key.pem`
## Default Environment Values
* `TZ = UTC` -> Set your own timezone
