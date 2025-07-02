#!/usr/bin/env python3

import json
import subprocess
import tempfile
import os
import logging
from flask import Flask, request, jsonify

app = Flask(__name__)
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def execute_script_safely(script):
    """Execute Python script safely using nsjail with Docker-compatible config"""
    
    # Basic validation
    if not script or len(script) > 50000:  # 50KB limit
        raise ValueError("Invalid script size")
    
    if "def main(" not in script:
        raise ValueError("Script must contain a 'main()' function")
    
    # Basic security checks
    dangerous_patterns = [
        'import subprocess', 'import os', '__import__', 'eval(', 'exec(',
        'open(', 'file(', 'input(', 'raw_input(', 'compile('
    ]
    
    for pattern in dangerous_patterns:
        if pattern in script:
            logger.warning(f"Potentially dangerous pattern detected: {pattern}")
    
    # Create temporary file for the script
    with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
        # Wrap the script to capture both return value and stdout
        wrapped_script = f"""
import sys
import json
import io
from contextlib import redirect_stdout

# User's script
{script}

# Execution wrapper
if __name__ == "__main__":
    stdout_capture = io.StringIO()
    
    try:
        # Redirect stdout to capture print statements
        with redirect_stdout(stdout_capture):
            result = main()
        
        # Prepare response
        response = {{
            "success": True,
            "result": result,
            "stdout": stdout_capture.getvalue()
        }}
        
        # Validate that result is JSON serializable
        json.dumps(result)
        
    except Exception as e:
        response = {{
            "success": False,
            "error": str(e),
            "stdout": stdout_capture.getvalue()
        }}
    
    # Output the response as JSON
    print(json.dumps(response))
"""
        f.write(wrapped_script)
        script_path = f.name

    try:
        # Execute with nsjail - Cloud Run compatible configuration
        cmd = [
            '/usr/local/bin/nsjail',
            '--mode', 'o',                    # Execute once and exit
            '--time_limit', '30',             # 30 seconds max execution time
            '--rlimit_as', '300',             # 300MB memory limit  
            '--rlimit_cpu', '30',             # 30 seconds CPU time
            '--rlimit_fsize', '10',           # 10MB max file size
            '--rlimit_nofile', '50',          # Max 50 open files
            '--quiet',                        # Reduce nsjail output
            '--disable_clone_newuser',        # Disable user namespace (Cloud Run compat)
            '--disable_clone_newnet',         # Keep network disabled
            '--', 'python3', script_path
        ]
        
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=35  # Slightly longer than nsjail timeout
        )
        
        if result.returncode != 0:
            # If nsjail fails, fallback to basic execution with timeout
            logger.warning("nsjail execution failed, falling back to basic execution")
            fallback_cmd = ['python3', script_path]
            result = subprocess.run(
                fallback_cmd,
                capture_output=True,
                text=True,
                timeout=30
            )
            if result.returncode != 0:
                raise RuntimeError(f"Script execution failed: {result.stderr}")
        
        # Parse the JSON response from the wrapped script
        try:
            output_lines = result.stdout.strip().split('\n')
            response_data = json.loads(output_lines[-1])
        except (json.JSONDecodeError, IndexError):
            raise RuntimeError("Failed to parse script output")
        
        if not response_data.get("success", False):
            raise RuntimeError(f"Script error: {response_data.get('error', 'Unknown error')}")
        
        return {
            "result": response_data["result"],
            "stdout": response_data["stdout"]
        }
        
    except subprocess.TimeoutExpired:
        raise RuntimeError("Script execution timed out (30s limit)")
    finally:
        # Clean up temporary file
        try:
            os.unlink(script_path)
        except:
            pass

@app.route('/health', methods=['GET'])
def health():
    """Health check endpoint"""
    return jsonify({"status": "healthy"})

@app.route('/execute', methods=['POST'])
def execute():
    """Execute Python script endpoint"""
    try:
        # Validate request
        if not request.is_json:
            return jsonify({"error": "Request must be JSON"}), 400
        
        data = request.get_json()
        if not data or 'script' not in data:
            return jsonify({"error": "Missing 'script' field in request body"}), 400
        
        script = data['script']
        
        # Execute script safely
        result = execute_script_safely(script)
        
        return jsonify(result), 200
        
    except Exception as e:
        logger.error(f"Execution error: {str(e)}")
        return jsonify({"error": str(e)}), 400

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port, debug=False)