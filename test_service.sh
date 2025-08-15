#!/bin/bash
# Build and test the service

# Build the Docker image
echo "Building Docker image..."
docker build -t python-execution-service .

# Run the service in the background
# Note: The Dockerfile and main.py have been configured to work without needing --privileged or --cap-add.
# However, if you encounter issues related to other restricted operations, you might need to add capabilities.
# Example (less secure): docker run -d -p 8080:8080 --cap-add=SYS_ADMIN --name test-service python-execution-service
# Example (least secure): docker run -d -p 8080:8080 --privileged --name test-service python-execution-service
echo "Starting service..."
docker run -d -p 8080:8080 --name test-service python-execution-service

# Wait for service to start
sleep 5

# Test the service
echo "Testing service..."
curl -X POST http://localhost:8080/execute \
  -H "Content-Type: application/json" \
  -d '{
    "script": "def main():\n    return {\"message\": \"Hello, World!\", \"value\": 42}"
  }'

echo -e "\nTest completed. Stopping service..."
docker stop test-service
docker rm test-service