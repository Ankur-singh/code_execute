import json
import logging
from flask import Flask, request, jsonify

from src.utils import validate_script, execute_script_safely
from src.config import DEBUG, DEFAULT_TIMEOUT, LOG_LEVEL

# Configure logging with the level from config
logging.basicConfig(level=getattr(logging, LOG_LEVEL, logging.INFO))
logger = logging.getLogger(__name__)
app = Flask(__name__)


@app.route("/execute", methods=["POST"])
def execute():
    try:
        # Get the JSON data from request
        data = request.get_json()

        if not data:
            return jsonify({"error": "No JSON data provided"}), 400

        script = data.get("script")
        timeout = data.get("timeout", DEFAULT_TIMEOUT)

        # Validate the script
        is_valid, error_msg = validate_script(script)
        if not is_valid:
            return jsonify({"error": error_msg}), 400

        # Execute the script safely
        stdout, stderr, returncode = execute_script_safely(script, timeout=timeout)
        logger.info(f"Return Code: {returncode}")
        logger.info(f"STDOUT: {stdout}")
        logger.info(f"STDERR: {stderr}")

        # Parse the result
        if returncode == 0:
            try:
                # The output should be a JSON string from our wrapper
                if stdout.strip():
                    result_data = json.loads(stdout.strip())
                    return jsonify(result_data)
                else:
                    return jsonify(
                        {
                            "error": "Script executed but returned no output",
                            "stdout": "",
                            "stderr": stderr,
                        }
                    ), 500
            except json.JSONDecodeError:
                # If not valid JSON, return as error
                return jsonify(
                    {
                        "error": "Script execution did not return valid JSON",
                        "stdout": stdout,
                        "stderr": stderr,
                    }
                ), 500
        else:
            # Execution failed
            # Try to parse error output as JSON first
            try:
                error_data = json.loads(stdout.strip())
                return jsonify(error_data), 500
            except (json.JSONDecodeError, ValueError):
                return jsonify(
                    {
                        "error": "Script execution failed",
                        "stdout": stdout,
                        "stderr": stderr,
                    }
                ), 500

    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}")
        return jsonify({"error": str(e)}), 500


@app.route("/health", methods=["GET"])
def health():
    return jsonify({"status": "healthy"})


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080, debug=DEBUG)
