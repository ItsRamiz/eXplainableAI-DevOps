import subprocess
from flask import request, jsonify, Response

visualization_process = None

def visualizeModelFunc(request):
    global visualization_process
    environment = request.form.get('environment')
    model = request.form.get('model')

    print(f"Environment: {environment}, Model: {model}")

    if environment == 'CrossingLava':
        env_name = 'MiniGrid-LavaCrossingS9N1-v0'
    else:
        env_name = 'MiniGrid-Unlock-v0'

    command = [
        'python', '-m', 'scripts.visualize',
        '--env', env_name,
        '--model', model
    ]

    print(f"Running command: {' '.join(command)}")

    def run_command(command):
        global visualization_process
        try:
            visualization_process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            for stdout_line in iter(visualization_process.stdout.readline, b""):
                yield stdout_line.decode()
            visualization_process.stdout.close()
            return_code = visualization_process.wait()
            if return_code:
                raise subprocess.CalledProcessError(return_code, command)
        except Exception as e:
            print(f"Error running command: {e}")
            yield str(e)

    return Response(run_command(command), mimetype='text/plain')

def kill_process():
    global visualization_process
    if visualization_process:
        visualization_process.terminate()
        visualization_process = None
        return jsonify(success=True, message="Visualization process terminated")
    else:
        return jsonify(success=False, message="No visualization process running")
