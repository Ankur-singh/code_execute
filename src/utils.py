import os
import logging
import tempfile
import subprocess

from src.config import PYTHON_PATH, LOG_LEVEL

# Configure logging with the level from config
logging.basicConfig(level=getattr(logging, LOG_LEVEL, logging.INFO))
logger = logging.getLogger(__name__)


# Add the execution code to capture the return value of main()
def wrap_script(script):
    return f"""
import sys
import json
{script}

# Capture stdout
import io
old_stdout = sys.stdout
sys.stdout = captured_stdout = io.StringIO()

try:
    # Execute main function and capture result
    result = main()

    # Get the captured stdout
    stdout_content = captured_stdout.getvalue()

    # Reset stdout
    sys.stdout = old_stdout

    # Output result as JSON
    output = {{
        "result": result,
        "stdout": stdout_content
    }}
    print(json.dumps(output))
except Exception as e:
    sys.stdout = old_stdout
    print(json.dumps({{"error": str(e)}}))
"""


def validate_script(script):
    """Validate the input script"""
    if not script:
        return False, "Script is empty"

    if not isinstance(script, str):
        return False, "Script must be a string"

    # Check if script contains a main function
    if "def main():" not in script:
        return False, "Script must contain a main() function"

    return True, ""


def execute_script_safely(script, timeout=60):
    """Execute the Python script in a secure environment using nsjail"""
    script = wrap_script(script)
    # Create a temporary file for the script
    with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
        f.write(script)
        script_path = f.name

    try:
        # Execute the script with nsjail
        cmd = [
            "nsjail",
            "--mode", "o",
            "--user", "9999",
            "--group", "9999",
            "--chroot", "/",
            "--time_limit", f"{timeout}",
            "--rlimit_as", "2048",
            "--rlimit_cpu", "10",
            "--rlimit_nofile", "64",
            "--rlimit_nproc", "100",
            "--disable_proc",
            "--really_quiet",
            "--",
            PYTHON_PATH, script_path
        ]
        
        # Run the command and capture output
        logger.info(f"Executing command: {' '.join(cmd)}")
        result = subprocess.run(
            cmd, capture_output=True, text=True, timeout=timeout + 5
        )

        return result.stdout, result.stderr, result.returncode
    except subprocess.TimeoutExpired:
        return "", "Script execution timed out", 1
    except FileNotFoundError:
        return "", "nsjail not found. Please ensure it is installed and in PATH", 1
    except Exception as e:
        logger.error(f"Error executing script: {str(e)}")
        return "", f"Error executing script: {str(e)}", 1
    finally:
        # Clean up temporary script file
        if os.path.exists(script_path):
            os.unlink(script_path)
