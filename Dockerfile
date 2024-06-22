# Use an appropriate base image
FROM python:3.12.4-alpine

# Set the timezone argument with a default value
ARG TZ=UTC

# Set default environment variable
ENV TZ=${TZ}

# Install necessary system dependencies and clean up in one layer
RUN apk add --no-cache tzdata && \
    cp /usr/share/zoneinfo/${TZ} /etc/localtime && \
    echo ${TZ} > /etc/timezone

# Copy the script into the container
COPY extract.py /extract.py

# Install Python dependencies with a pinned version
RUN pip install --no-cache-dir watchdog tzlocal

# Add metadata to the image
LABEL org.opencontainers.image.description="First release on new base. Thanks to @waschinski for the help."

# Command to run the script
CMD ["python", "/extract.py", "--restart", "unless-stopped"]
