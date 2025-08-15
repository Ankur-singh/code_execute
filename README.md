# Secure Python Script Execution Service

This service allows secure execution of arbitrary Python scripts in an isolated environment using Flask and nsjail.

### Features

- Secure script execution using Linux namespaces (nsjail)
- JSON API for script submission and result retrieval
- Support for popular libraries (numpy, pandas)

### Requirements

- Docker (for containerized deployment)
- nsjail (installed automatically in Docker image)

### Quick test

```bash
./test_service.sh
```

## Running the Service


### Using Docker (Recommended)

Build the image (multi-stage, minimal final image):
```bash
docker build -t python-execution-service .
```

Run the service (with nsjail sandboxing):
```bash
docker run --privileged -p 8080:8080 --rm -e DEBUG=1 python-execution-service
```

**Security Note:** The `--privileged` flag is required for nsjail to function fully. For production, review nsjail and Docker security documentation to minimize risk.

The container runs as a non-root user (`sandboxuser`) for improved security.

### Running Locally

1. Install nsjail (follow instructions at https://github.com/google/nsjail)

2. Install dependencies:
    ```bash
    pip install -r requirements.txt numpy pandas
    ```

3. Set `PYTHON_PATH` to point to your local Python interpreter if necessary:
    ```bash
    export PYTHON_PATH=$(which python)
    ```

    > ⚠️ **Note**: If you are using a virtual environment, make sure it is activated before running the above command.

4. Run the service:
    ```bash
    DEBUG=1 python -m src.main
    ```

## API Usage

```bash
curl -X GET http://localhost:8080/health
```

```bash
curl -X POST http://localhost:8080/execute \
  -H "Content-Type: application/json" \
  -d '{
    "script": "def main():\n    import numpy as np\n    arr = np.array([1, 2, 3, 4, 5])\n    print(\"This will not be in the result\")\n    return {\"sum\": int(np.sum(arr)), \"mean\": float(np.mean(arr))}"
  }'
```

Example response:
```json
{
  "result": {
    "sum": 15,
    "mean": 3.0
  },
  "stdout": "This will not be in the result\n"
}
```

