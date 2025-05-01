import os
import subprocess
from flask import Flask, json, jsonify, request, send_file, after_this_request
from pathlib import Path
import shutil, sys
import zipfile
from run import execute_command
from flask_cors import CORS


app = Flask(__name__, template_folder='templates')
CORS(app)
app.secret_key = 'your_secret_key' 
 

@app.route('/train', methods=['POST'])
def handle_train():
    
    data = request.get_json()
    command = data.get("command")
    rc = execute_command(command)

    gif_path = "Generated.gif"
    
    return send_file(gif_path, mimetype="image/gif")



@app.route('/train_custom', methods=['POST'])
def handle_train_custom():
    data = request.get_json()
    command = data.get("command")
    environment_data = data.get("environment_data")

    if environment_data:
        env_path = os.path.join('customEnvs', 'environment.json')
        os.makedirs('customEnvs', exist_ok=True)
        with open(env_path, 'w') as f:
            json.dump(environment_data, f)
        print("Environment data saved to", env_path)

    rc = execute_command(command)

    gif_path = "Generated.gif"
    return send_file(gif_path, mimetype="image/gif")




@app.route('/list_agents', methods=['GET'])
def list_agents():
    agents_dir = os.path.join('storage')
    try:
        agents = [name for name in os.listdir(agents_dir) if os.path.isdir(os.path.join(agents_dir, name))]
        return jsonify(agents=agents), 200
    except Exception as e:
        return jsonify(error=str(e)), 500


@app.route('/visualize', methods=['POST'])
def handle_visualize():
    data = request.get_json()
    command = data.get("command")

    print("Received command:", command)

    rc = execute_command(command)

    gif_path = "Generated.gif"
    try:
        return send_file(gif_path, mimetype="image/gif")
    except Exception as e:
        print("Failed to send file:", e)
        return "Failed to return image", 500


@app.route('/download', methods=['GET'])
def download_model():
    model_name = request.args.get('model') + "_model"
    models_dir = os.path.join(os.path.dirname(__file__), 'storage')
    model_path = os.path.join(models_dir, model_name)
    zip_path = os.path.join(models_dir, f"{model_name}.zip")

    if not os.path.exists(model_path):
        return f"Model file or folder '{model_name}' not found", 404

    # Create zip file
    try:
        with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
            if os.path.isdir(model_path):
                for root, _, files in os.walk(model_path):
                    for file in files:
                        full_path = os.path.join(root, file)
                        arcname = os.path.relpath(full_path, model_path)
                        zipf.write(full_path, arcname)
            else:
                zipf.write(model_path, os.path.basename(model_path))
    except Exception as e:
        print("Error zipping model:", e)
        return "Failed to zip model", 500

    # Cleanup after sending file
    @after_this_request
    def cleanup(response):
        try:
            if os.path.isdir(model_path):
                shutil.rmtree(model_path)
            if os.path.exists(zip_path):
                os.remove(zip_path)
        except Exception as cleanup_error:
            print("Cleanup failed:", cleanup_error)
        return response

    return send_file(zip_path, as_attachment=True)

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5001)

