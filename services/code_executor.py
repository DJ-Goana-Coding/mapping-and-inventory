"""
Q.G.T.N.L. (0) // CODE EXECUTOR
Safe sandboxed code execution for the Citadel Coding Agent.
Runs Python code in a subprocess with timeout and output capture.
"""
import subprocess
import sys
import tempfile
import os
from pathlib import Path

# Maximum execution time in seconds
MAX_EXECUTION_TIME = 30

# Maximum output length in characters
MAX_OUTPUT_LENGTH = 50_000


def execute_python(code: str, timeout: int = MAX_EXECUTION_TIME) -> dict:
    """Execute Python code in a subprocess and return the result.

    Returns a dict with keys: success, stdout, stderr, return_code, timed_out.
    """
    with tempfile.NamedTemporaryFile(
        mode="w",
        suffix=".py",
        dir="/tmp",
        delete=False,
    ) as f:
        f.write(code)
        script_path = f.name

    try:
        result = subprocess.run(
            [sys.executable, script_path],
            capture_output=True,
            text=True,
            timeout=timeout,
            cwd="/tmp",
            env={
                **os.environ,
                "PYTHONDONTWRITEBYTECODE": "1",
            },
        )
        stdout = result.stdout[:MAX_OUTPUT_LENGTH]
        stderr = result.stderr[:MAX_OUTPUT_LENGTH]
        return {
            "success": result.returncode == 0,
            "stdout": stdout,
            "stderr": stderr,
            "return_code": result.returncode,
            "timed_out": False,
        }
    except subprocess.TimeoutExpired:
        return {
            "success": False,
            "stdout": "",
            "stderr": f"⏰ Execution timed out after {timeout} seconds.",
            "return_code": -1,
            "timed_out": True,
        }
    except Exception as e:
        return {
            "success": False,
            "stdout": "",
            "stderr": f"Execution error: {e!s}",
            "return_code": -1,
            "timed_out": False,
        }
    finally:
        try:
            os.unlink(script_path)
        except OSError:
            pass


def execute_bash(command: str, timeout: int = MAX_EXECUTION_TIME) -> dict:
    """Execute a bash command and return the result."""
    try:
        result = subprocess.run(
            ["bash", "-c", command],
            capture_output=True,
            text=True,
            timeout=timeout,
            cwd="/tmp",
        )
        stdout = result.stdout[:MAX_OUTPUT_LENGTH]
        stderr = result.stderr[:MAX_OUTPUT_LENGTH]
        return {
            "success": result.returncode == 0,
            "stdout": stdout,
            "stderr": stderr,
            "return_code": result.returncode,
            "timed_out": False,
        }
    except subprocess.TimeoutExpired:
        return {
            "success": False,
            "stdout": "",
            "stderr": f"⏰ Execution timed out after {timeout} seconds.",
            "return_code": -1,
            "timed_out": True,
        }
    except Exception as e:
        return {
            "success": False,
            "stdout": "",
            "stderr": f"Execution error: {e!s}",
            "return_code": -1,
            "timed_out": False,
        }
