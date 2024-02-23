#!/bin/bash

# Set your Docker Compose file path
DOCKER_COMPOSE_FILE="/home/ubuntu/it-chatbot/openai-trulens-hackathon/docker-compose.yml"

# Set any additional Docker Compose options
DOCKER_COMPOSE_OPTIONS="--detach"  # Use "--detach" to run containers in the background

docker-compose -f $DOCKER_COMPOSE_FILE down

git pull
echo "pulled successfully.!"

# Build and run with Docker Compose
echo "Building and running with Docker Compose..."
docker-compose -f $DOCKER_COMPOSE_FILE build
docker-compose -f $DOCKER_COMPOSE_FILE up $DOCKER_COMPOSE_OPTIONS

echo "Deployment complete!"
