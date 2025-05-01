import os, requests
import subprocess
import json
from flask import jsonify, request

def process_training_request(form_data):
    data = {
        'environment': form_data.get('EnvName') or 'Unlock',
        'agentName': form_data.get('agentName') or 'default_agent',
        'seed': form_data.get('seed') or 1,
        'processes': form_data.get('processes') or 16,
        'frames': form_data.get('frames') or 1,
        'epochs': form_data.get('epochs') or 4,
        'batchSize': form_data.get('batchSize') or 256,
        'discount': form_data.get('discount') or 0.99,
        'learningRate': form_data.get('learningRate') or 0.001,
        'entropyCoef': form_data.get('entropyCoef') or 0.01,
        'adamEpsilon': form_data.get('adamEpsilon') or 1e-8,
        'rmspropOptimizer': form_data.get('rmspropOptimizer') or 0.99,
        'timeSteps': form_data.get('timeSteps') or 1,
        'maxNorm': form_data.get('maxNorm') or 0.5,
        'customCommand': form_data.get('customCommand') or None
    }

    # Convert to appropriate data types
    data['seed'] = int(data['seed'])
    data['processes'] = int(data['processes'])
    data['frames'] = int(data['frames'])
    data['epochs'] = int(data['epochs'])
    data['batchSize'] = int(data['batchSize'])
    data['discount'] = float(data['discount'])
    data['learningRate'] = float(data['learningRate'])
    data['entropyCoef'] = float(data['entropyCoef'])
    data['adamEpsilon'] = float(data['adamEpsilon'])
    data['rmspropOptimizer'] = float(data['rmspropOptimizer'])
    data['timeSteps'] = int(data['timeSteps'])
    data['maxNorm'] = float(data['maxNorm'])

    command = [
        'python', '-m', 'scripts.train',
        '--algo', 'ppo',
        '--env', data['environment'],
        '--model', data['agentName'],
        '--save-interval', '100',
        '--frames', str(data['frames']),
        '--lr', str(data['learningRate']),
        '--batch-size', str(data['batchSize']),
        '--epochs', str(data['epochs']),
        '--frames-per-proc', '128',
        '--discount', str(data['discount']),
        '--gae-lambda', '0.95',
        '--entropy-coef', str(data['entropyCoef']),
        '--value-loss-coef', '0.5',
        '--max-grad-norm', str(data['maxNorm']),
        '--clip-eps', '0.2',
        '--procs', str(data['processes']),
        '--custom', '1'
    ]

    if data['customCommand']:
        command.extend(data['customCommand'].split())

    try:
        # Load the custom environment data
        with open('customEnvs/environment.json', 'r') as f:
            env_json = json.load(f)

        # Send both command and env_json to the backend
        response = requests.post(
            "http://backend:5001/train_custom",
            json={
                "command": command,
                "environment_data": env_json
            }
        )

        if response.status_code == 200:
            gif_path = os.path.join('static', 'output.gif')
            with open(gif_path, 'wb') as f:
                f.write(response.content)

            return {"status": "success", "message": "Training completed and GIF saved."}
        else:
            return {"status": "error", "message": f"Training failed with code {response.status_code}"}

    except Exception as e:
        return {"status": "error", "message": str(e)}


def execute_command(command):
    try:
        process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        stdout, stderr = process.communicate()

        if process.returncode == 0:
            return 0
        else:
            error_message = stderr.decode()
            return error_message
    except subprocess.CalledProcessError as e:
        return str(e)


