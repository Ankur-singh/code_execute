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

```bash
docker build -t python-execution-service .
docker run --privileged -p 8080:8080 python-execution-service
```

### Running Locally

1. Install nsjail (follow instructions at https://github.com/google/nsjail)

2. Install dependencies:
    ```bash
    pip install -r requirements.txt
    ```

3. Ensure you have numpy and pandas installed
    ```bash
    pip install numpy pandas
    ```

4. Update the python path in `app/utils.py` to point to your local Python interpreter if necessary.
    ```bash
    sed -i "s|/usr/local/bin/python|$(which python)|g" app/utils.py
    ```

    > ⚠️ **Note**: Remember to revert back this change after testing. Else it will break the code.

    > ⚠️ **Note**: If you are using a virtual environment, make sure it is activated before running the above command.

5. Run the service:
    ```bash
    python -m app.main
    ```

## API Usage

### Execute a Python Script

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

