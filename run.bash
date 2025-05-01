set -e  # Exit on any error

read -p "Enter your Docker Hub username: " DOCKER_USER
DOCKER_USER=${DOCKER_USER:-yourdefaultusername}

echo "Terraform Init & Apply"
cd terraform
terraform init
terraform apply -auto-approve
cd ..

echo "Docker Compose Build"
echo "Backend Includes NVIDIA CUDA Libraries - approx 10 mintues."
docker-compose build

echo "Pushing Docker Images"
docker tag devopslocal-frontend $DOCKER_USER/frontend:latest
docker tag devopslocal-backend $DOCKER_USER/backend:latest
docker push $DOCKER_USER/frontend:latest
docker push $DOCKER_USER/backend:latest

echo "☸️  Step 4: Kubernetes Apply"
kubectl apply -f k8s/

echo "Deployment Complete!"
