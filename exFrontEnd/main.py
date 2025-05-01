import os, time
from flask import Flask, json, jsonify, render_template, request, redirect, url_for, flash
from agents.visualizeModel import visualizeModelFunc
from agents.trainingParameters import submit_training_agent, training_status_func
from agents.visulizationPage import visualizeModelFunction
from customEnvs.trainCustomEnv import process_training_request
from aws_utils.dbManager import list_agents, fetch_ImageURLS, fetch_IconURLS

app = Flask(__name__, template_folder='templates')
app.secret_key = 'your_secret_key' 

visualization_process = None  
env_data_path = os.path.join(app.root_path, 'customEnvs/environment.json')
storage_folder = 'storage'  

# Main page
@app.route('/')
def index():

    signed_images = fetch_ImageURLS()

    gif_path = os.path.join('static', 'output.gif')
    if os.path.exists(gif_path):
        try:
            os.remove(gif_path)
            print("Deleted existing output.gif")
        except Exception as e:
            print("Failed to delete output.gif:", e)
    return render_template('MAIN.html', images = signed_images)


# Training routes
@app.route('/training')
def training():
    return render_template('modelTraining.html')

@app.route('/submit_training', methods=['POST'])
def submit_training():
    return submit_training_agent(request)

@app.route('/training_process')
def training_process():
    return render_template('trainingProcess.html')

@app.route('/training_status')
def training_status():
    return training_status_func()

@app.route('/visualize', methods=['POST'])
def visualize():
    return visualizeModelFunc(request)

# visualization page routes
@app.route('/visualizePage')
def visualizePage():
    gif_path = os.path.join('static', 'output.gif')
    gif_exists = os.path.exists(gif_path)
    timestamp = int(time.time())  # Cache buster
    return render_template('visulize.html', gif_exists=gif_exists, timestamp=timestamp)

@app.route('/visualizeFunc', methods=['POST'])
def visualizeFunc():
    return visualizeModelFunction(request)

# custom environment page routes
@app.route('/CustomEnvPage')
def CustomEnvPage():
    return render_template('CustomEnv.html')

@app.route('/trainCustomEnvPage')
def trainCustomEnvPage():
    return render_template('trainCustomEnv.html')

@app.route('/save-environment', methods=['POST'])
def save_environment():
    data = request.json
    with open(env_data_path, 'w') as file:
        json.dump(data, file)

    return jsonify({"status": "success", "message": "Environment saved!"})

@app.route('/view-training-gif')
def view_training_gif():
    import time
    return render_template('view_gif.html', timestamp=int(time.time()))

@app.route('/submit_custom_training', methods=['POST'])
def submit_custom_training():
    form_data = request.form.to_dict()  
    result = process_training_request(form_data)
    agent_folder_name = form_data.get('agentName') or 'default_agent'
    folder_path = os.path.join(storage_folder, agent_folder_name)
    zip_filename = f"{agent_folder_name}.zip"
    zip_filepath = os.path.join(storage_folder, zip_filename)

    if result['status'] == 'success':
        return redirect(url_for('view_training_gif'))

    else:
        flash(result['message'], 'error')
        return redirect(url_for('trainCustomEnvPage'))


if __name__ == "__main__":

    app.run(debug=True, host="0.0.0.0", port=5000)
