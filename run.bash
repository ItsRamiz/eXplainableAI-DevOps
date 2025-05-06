#!/bin/bash
set -e  # Exit on any error

read -p "Enter your Docker Hub username: " DOCKER_USER
DOCKER_USER=${DOCKER_USER:-yourdefaultusername}

echo "Terraform Init & Apply"
cd terraform
terraform init
if [ $? -ne 0 ]; then
  echo "Error: Terraform init failed."
  exit 1
fi

terraform apply -auto-approve
if [ $? -ne 0 ]; then
  echo "Error: Terraform apply failed."
  exit 1
fi
cd ..

echo "Docker Compose Build"
echo "Backend includes NVIDIA CUDA libraries — may take up to 10 minutes."
docker-compose build
if [ $? -ne 0 ]; then
  echo "Error: Docker build failed."
  exit 1
fi

echo "Tagging and Pushing Docker Images"
docker tag devopslocal-frontend $DOCKER_USER/frontend:latest
docker tag devopslocal-backend $DOCKER_USER/backend:latest

docker push $DOCKER_USER/frontend:latest
if [ $? -ne 0 ]; then
  echo "Error: Failed to push frontend image."
  exit 1
fi

docker push $DOCKER_USER/backend:latest
if [ $? -ne 0 ]; then
  echo "Error:
