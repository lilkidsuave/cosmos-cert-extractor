# Use an appropriate base image and pin a specific version of Alpine
FROM python:3.12-alpine
# Set the timezone argument with a default value
ARG TZ=UTC
# Set default environment variable
ENV TZ=${TZ}
# Install necessary system dependencies and clean up in one layer
RUN apk add --no-cache tzdata \
    && cp /usr/share/zoneinfo/${TZ} /etc/localtime \
    && echo ${TZ} > /etc/timezone \
    && pip install --no-cache-dir watchdog==4.0.1 tzlocal==5.2
# Copy the script into the container
COPY extract.py /extract.py
# Add metadata to the image
LABEL org.opencontainers.image.description="First release on new base. Thanks to @waschinski for the help."
# Command to run the script
ENTRYPOINT ["python", "/extract.py"]
