import os
import subprocess
import time

def execute_command(command):
    global training_status
    print("Executing ---> ")
    print(command)
    try:
        process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        while True:
            output = process.stdout.readline()
            if output == b'' and process.poll() is not None:
                break
            if output:
                print(output.strip().decode())
                time.sleep(1)
        rc = process.poll()
        return rc
    except subprocess.CalledProcessError as e:
        return str(e)