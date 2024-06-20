# Use an appropriate base image
FROM python:3.12-slim
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    tzdata && \
    rm -rf /var/lib/apt/lists/*
# Copy the script into the container
COPY extract.py /extract.py 
# Install any necessary dependencies
RUN pip install pyOpenSSL watchdog pytz tzlocal
# Set default environment variable
ENV CHECK_INTERVAL=0
ENV WATCHDOG_ENABLED=true
ENV TZ=EST
RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone
# Make sure the script is executable (if necessary)
RUN chmod +x /extract.py
# Command to run the script
ENTRYPOINT ["./extract.py"]
