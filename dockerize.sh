#!/bin/bash

# Define the image name and container name
IMAGE_NAME="pricer"
CONTAINER_NAME="pricer-container"

# Trap SIGINT (Ctrl+C) to stop the container and exit
trap 'echo "Stopping container..."; docker stop $CONTAINER_NAME > /dev/null 2>&1; exit 0' SIGINT

# Run the Docker container in detached mode first to get a container ID
echo "Starting Docker container..."
docker run --name $CONTAINER_NAME -p 8000:8000 $IMAGE_NAME &

# Monitor and wait for Ctrl+C
echo "Docker container is running. Press Ctrl+C to stop."
while true; do
    sleep 1  # Keeps the script alive
done