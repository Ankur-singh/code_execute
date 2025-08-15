# Secure Python Script Execution Service

This service allows secure execution of arbitrary Python scripts in an isolated environment using Flask and nsjail.

## Features

- Secure script execution using Linux namespaces (nsjail)
- JSON API for script submission and result retrieval
- Support for popular libraries (numpy, pandas)

## Running the Service

### Using Docker (Recommended)

```bash
docker build -t python-execution-service .
docker run -p 8080:8080 python-execution-service
```

### Running Locally

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Install nsjail (follow instructions at https://github.com/google/nsjail)

3. Run the service:
```bash
python app/main.py
```

## API Usage

### Execute a Python Script

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

### Cloud Run Example

```bash
curl -X POST https://python-execution-service-xyz123.a.run.app/execute \
  -H "Content-Type: application/json" \
  -d '{
    "script": "def main():\n    import pandas as pd\n    df = pd.DataFrame({\"A\": [1, 2, 3], \"B\": [4, 5, 6]})\n    return df.to_dict()"
  }'
```

## Requirements

- Python 3.9+
- Docker (for containerized deployment)
- nsjail (installed automatically in Docker image)

## Supported Libraries

- Standard Python library
- numpy
- pandas