#!/bin/bash

# Build the Docker image
echo "Building Docker image..."
docker build -t python-execution-service .

# Run the service in the background
# nsjail requires allivated permission for some restricted operations, you might need to add capabilities.
# Less secure: docker run -d -p 8080:8080 --cap-add=SYS_ADMIN --name test-service python-execution-service
# Least secure: docker run -d -p 8080:8080 --privileged --name test-service python-execution-service
echo "Starting service..."
docker run --privileged -d -p 8080:8080 --name test-service python-execution-service

# Wait for service to start
sleep 5

# Test the service
echo "Testing service..."
curl -X POST http://localhost:8080/execute \
  -H "Content-Type: application/json" \
  -d '{
    "script": "def main():\n    return {\"message\": \"Hello, World!\", \"value\": 42}"
  }'

curl -X POST http://localhost:8080/execute \
  -H "Content-Type: application/json" \
  -d '{
    "script": "def main():\n    import numpy as np\n    arr = np.array([1, 2, 3, 4, 5])\n    print(\"This will not be in the result\")\n    return {\"sum\": int(np.sum(arr)), \"mean\": float(np.mean(arr))}"
  }'

curl -X POST http://localhost:8080/execute \
  -H "Content-Type: application/json" \
  -d '{
    "script": "def main():\n    import pandas as pd\n    df = pd.DataFrame({\"A\": [1, 2, 3], \"B\": [4, 5, 6]})\n    return df.to_dict()"
  }'

echo -e "\nTest completed. Stopping service..."
docker stop test-service
docker rm test-service