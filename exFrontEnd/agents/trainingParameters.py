import os
import subprocess
import json
from flask import jsonify, Response
import time, requests

training_status = {'progress': 0}

def submit_training_agent(request):
    global training_status
    if request.method == 'POST':
        data = {
            'environment': request.form.get('environment') or 'Unlock',
            'addMemory': request.form.get('addMemory') == 'on',
            'agentName': request.form.get('agentName') or 'default_agent',
            'seed': request.form.get('seed') or 1,
            'processes': request.form.get('processes') or 16,
            'frames': request.form.get('frames') or 1,
            'epochs': request.form.get('epochs') or 4,
            'batchSize': request.form.get('batchSize') or 256,
            'discount': request.form.get('discount') or 0.99,
            'learningRate': request.form.get('learningRate') or 0.001,
            'entropyCoef': request.form.get('entropyCoef') or 0.01,
            'adamEpsilon': request.form.get('adamEpsilon') or 1e-8,
            'rmspropOptimizer': request.form.get('rmspropOptimizer') or 0.99,
            'timeSteps': request.form.get('timeSteps') or 1,
            'maxNorm': request.form.get('maxNorm') or 0.5,
            'customCommand': request.form.get('customCommand') or None
        }

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

        with open('agents/training_data.json', 'w') as f:
            json.dump(data, f)

        command = build_training_command(data)

        training_status = {'progress': 0}
        
        response = requests.post("http://backend:5001/train", json={"command": command})

        if response.status_code == 200:
            # Save the received GIF
            gif_filename = f"static/output.gif"
            with open(gif_filename, "wb") as f:
                f.write(response.content)

            training_status['progress'] = 100

            return jsonify(success=True, modelName=data['agentName'], gifPath=f"/{gif_filename}")
        
        else:
            return jsonify(success=False, error="Training failed", status_code=response.status_code)

def build_training_command(data):
    if data['customCommand']:
        command = data['customCommand'].split()
    else:
        env_map = {
            'Unlock': 'MiniGrid-Unlock-v0',
            'CrossingLava': 'MiniGrid-LavaCrossingS9N1-v0'
        }

        environment = env_map.get(data['environment'], 'MiniGrid-Unlock-v0')
        model_name = f"{data['agentName']}_model"  

        command = [
            'python', '-m', 'scripts.train',
            '--algo', 'ppo',
            '--env', environment,
            '--model', model_name,
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
            '--procs', str(data['processes'])
        ]

        if data.get('seed'):
            command += ['--seed', str(data['seed'])]

    return command

def execute_command(command):
    global training_status
    print("Started Train")
    try:
        process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        while True:
            output = process.stdout.readline()
            if output == b'' and process.poll() is not None:
                break
            if output:
                print(output.strip().decode())
                training_status['progress'] += 10
                time.sleep(1)
        rc = process.poll()
        return rc
    except subprocess.CalledProcessError as e:
        return str(e)

def training_status_func():
    global training_status
    return jsonify(training_status)
