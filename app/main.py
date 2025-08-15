import os
import json
import tempfile
import subprocess
from flask import Flask, request, jsonify

app = Flask(__name__)

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

def execute_script_safely(script_content):
    """Execute the Python script in a secure environment using nsjail"""
    # Create a temporary file for the script
    with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
        f.write(script_content)
        script_path = f.name
    
    try:
        # Execute the script with nsjail
        # nsjail --user 99999 --group 99999 --disable_proc --chroot / --really_quiet
        # Disable namespace cloning that is restricted inside Docker containers
        cmd = [
            'nsjail',
            '--mode', 'o',
            '--user', '9999',
            '--group', '9999',
            '--chroot', '/',
            '--time_limit', '30',
            '--rlimit_as', '2048',
            '--rlimit_cpu', '10',
            '--rlimit_nofile', '64',
            '--rlimit_nproc', '10',
            '--disable_proc',
            '--really_quiet',
            # '--disable_clone_newuser',  # Disable user namespace cloning (restricted in Docker)
            # '--disable_clone_newpid',   # Disable PID namespace cloning (restricted in Docker)
            # '--disable_clone_newnet',   # Disable network namespace cloning (restricted in Docker)
            '--',
            '/usr/bin/python3', script_path
        ]
        
        # Run the command and capture output
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=60
        )
        
        return result.stdout, result.stderr, result.returncode
    finally:
        # Clean up temporary script file
        if os.path.exists(script_path):
            os.unlink(script_path)

@app.route('/execute', methods=['POST'])
def execute():
    try:
        # Get the JSON data from request
        data = request.get_json()
        
        if not data:
            return jsonify({"error": "No JSON data provided"}), 400
        
        script = data.get('script')
        
        # Validate the script
        is_valid, error_msg = validate_script(script)
        if not is_valid:
            return jsonify({"error": error_msg}), 400
        
        # Add the execution code to capture the return value of main()
        wrapped_script = f"""
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

        # Execute the script safely
        stdout, stderr, returncode = execute_script_safely(wrapped_script)
        print(f"Script executed with return code: {returncode}")
        print(f"STDOUT: {stdout}")
        print(f"STDERR: {stderr}")

        # Parse the result
        if returncode == 0:
            try:
                # The output should be a JSON string from our wrapper
                if stdout.strip():
                    result_data = json.loads(stdout.strip())
                    return jsonify(result_data)
                else:
                    return jsonify({
                        "error": "Script executed but returned no output",
                        "stdout": "",
                        "stderr": stderr
                    }), 500
            except json.JSONDecodeError:
                # If not valid JSON, return as error
                return jsonify({
                    "error": "Script execution did not return valid JSON",
                    "stdout": stdout,
                    "stderr": stderr
                }), 500
        else:
            # Execution failed
            # Try to parse error output as JSON first
            try:
                error_data = json.loads(stdout.strip())
                return jsonify(error_data), 500
            except (json.JSONDecodeError, ValueError):
                return jsonify({
                    "error": "Script execution failed",
                    "stdout": stdout,
                    "stderr": stderr
                }), 500
            
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/health', methods=['GET'])
def health():
    return jsonify({"status": "healthy"})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080, debug=True)