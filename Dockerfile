# Use an appropriate base image
FROM python:3.12-slim
RUN apt-get update -y
RUN apt-get install -y tzdata
# Copy the script into the container
COPY extract.py /extract.py 
# Install any necessary dependencies
RUN pip install pyOpenSSL watchdog pytz tzlocal
# Set default environment variable
ENV CHECK_INTERVAL=0
ENV WATCHDOG_ENABLED=true
# Make sure the script is executable (if necessary)
RUN chmod +x /extract.py
# Command to run the script
ENTRYPOINT ["./extract.py"]
