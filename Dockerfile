# Use an appropriate base image and pin a specific version of Alpine
FROM alpine:3.20
# Set the timezone argument with a default value
ARG TZ=UTC
# Set default environment variable
ENV TZ=${TZ}
# Install necessary system dependencies and clean up in one layer
RUN apk add --no-cache tzdata \
    && cp /usr/share/zoneinfo/${TZ} /etc/localtime \
    && echo ${TZ} > /etc/timezone
# Copy the script into the container
COPY extract.sh /extract.sh
# Add metadata to the image
LABEL org.opencontainers.image.description="First release on new base. Thanks to @waschinski for the help."
# Command to run the script
ENTRYPOINT ["sh", "/extract.sh"]
