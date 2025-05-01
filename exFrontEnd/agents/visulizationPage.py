import os
import subprocess
from flask import redirect, url_for, jsonify, request
import requests

visualization_process = None  

def visualizeModelFunction(request):
    selected_folder = request.form.get('selectAgent')
    if not selected_folder:
        return redirect(url_for('visualizePage'))

    model = selected_folder
    env_name = extractEnvNameFromFolder(selected_folder)
    if not env_name:
        return redirect(url_for('visualizePage'))

    command = [
        'python', '-m', 'scripts.visualize',
        '--env', env_name,
        '--model', model
    ]

    try:
        response = requests.post("http://backend:5001/visualize", json={"command": command})
        if response.status_code == 200:
            gif_filename = f"static/output.gif"
            with open(gif_filename, "wb") as f:
                f.write(response.content)

            return redirect(url_for('visualizePage'))  # or render a success page
        else:
            print("Error:", response.status_code)
            return redirect(url_for('visualizePage'))
    except Exception as e:
        print("Request failed:", e)
        return redirect(url_for('visualizePage'))
    

def killDisplayFunc():
    global visualization_process

    if visualization_process:
        try:
            visualization_process.terminate()  
            visualization_process = None
        except Exception as e:
            pass

    return redirect(url_for('visualizePage'))

def extractEnvNameFromFolder(folder_name):
    log_file_path = os.path.join('storage', folder_name, 'log.txt')
    if not os.path.exists(log_file_path):
        return None

    env_name = None
    with open(log_file_path, 'r') as log_file:
        for line in log_file:
            if '--env' in line:
                env_name = line.split('--env')[1].split()[0]
                break

    return env_name

def getFolders():
    storage_path = 'storage'
    folders = [name for name in os.listdir(storage_path) if os.path.isdir(os.path.join(storage_path, name))]
    return jsonify(folders)
