import subprocess
import json
import logging

logger = logging.getLogger("docker_utils")

def execute_docker_command(command: list) -> str:
    """Executes a docker command and returns the stdout."""
    try:
        result = subprocess.run(
            ['docker'] + command,
            capture_output=True,
            text=True,
            check=True
        )
        return result.stdout
    except subprocess.CalledProcessError as e:
        logger.error(f"Docker command failed: {' '.join(command)}")
        logger.error(f"stdout: {e.stdout}")
        logger.error(f"stderr: {e.stderr}")
        raise RuntimeError(f"Docker command failed: {e.stderr}")

def get_local_models() -> list:
    """Lists local models available via DMR."""
    output = execute_docker_command(['model', 'ls', '--format', 'json'])
    return [json.loads(line) for line in output.strip().split('\n') if line]

def pull_model(model_ref: str, progress_callback=None):
    """Pulls a model using DMR."""
    logger.info(f"Attempting to pull model: {model_ref}")
    process = subprocess.Popen(
        ['docker', 'model', 'pull', model_ref],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        bufsize=1
    )
    # Stream output to the console or a callback
    while True:
        output = process.stdout.readline()
        if output == '' and process.poll() is not None:
            break
        if output:
            logger.info(output.strip())
            if progress_callback:
                progress_callback(output.strip())
    
    if process.returncode != 0:
        stderr_output = process.stderr.read()
        logger.error(f"Model pull failed for {model_ref}: {stderr_output}")
        raise RuntimeError(f"Model pull failed: {stderr_output}")

def run_model(model_ref: str, input_data: str) -> str:
    """Runs a model using DMR and returns the output."""
    logger.info(f"Running model {model_ref} with input: {input_data[:50]}...")
    output = execute_docker_command(['model', 'run', model_ref, '--', input_data])
    return output