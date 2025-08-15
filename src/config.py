import os

# Configuration settings
DEBUG = int(os.getenv("DEBUG", "0")) != 0
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO").upper()
DEFAULT_TIMEOUT = int(os.getenv("DEFAULT_TIMEOUT", "60"))
PYTHON_PATH = os.getenv("PYTHON_PATH", "/usr/local/bin/python")