# Use an appropriate base image
FROM python:3.12-slim
# Copy the script into the container
COPY extract.py /extract.py 
# Install any necessary dependencies
RUN pip install pyOpenSSL watchdog pytz hashlib
# Set default environment variable
ENV CHECK_INTERVAL=0
ENV WATCHDOG_ENABLED=true
ENV TIMEZONE=UTC
# Make sure the script is executable (if necessary)
RUN chmod +x /extract.py
# Command to run the script
ENTRYPOINT ["./extract.py"]
