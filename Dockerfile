# Use an appropriate base image
FROM python:3.12.4-slim

# Set the timezone argument with a default value
ARG TZ=UTC

# Set default environment variable
ENV TZ=${TZ}

# Install necessary system dependencies and clean up in one layer
RUN apt-get update && \
    apt-get install -y --no-install-recommends tzdata && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Copy the script into the container
COPY extract.py /extract.py

# Install Python dependencies
RUN pip install --no-cache-dir watchdog tzlocal

# Add metadata to the image
LABEL org.opencontainers.image.description="First release on new base. Thanks to @waschinski for the help."

# Command to run the script
CMD ["python", "/extract.py", "--restart", "unless-stopped"]
