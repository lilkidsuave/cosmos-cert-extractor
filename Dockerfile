# Use an appropriate base image for Debian Slim with a specific Python version
FROM python:3.12-slim
# Set the timezone argument with a default value (if needed)
ARG TZ=UTC
# Set default environment variable for timezone
ENV TZ=${TZ}
# Install necessary system dependencies and clean up in one layer
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        tzdata && \
    ln -fs /usr/share/zoneinfo/$TZ /etc/localtime && \
    echo $TZ > /etc/timezone && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*
# Install Python packages with specific versions
RUN pip install --no-cache-dir watchdog==4.0.1 tzlocal==5.2
# Copy the script into the container
COPY extract.py /extract.py
# Add metadata to the image
LABEL org.opencontainers.image.description="First release on new base. Thanks to @waschinski for the help."
# Command to run the script
ENTRYPOINT ["python", "/extract.py"]
