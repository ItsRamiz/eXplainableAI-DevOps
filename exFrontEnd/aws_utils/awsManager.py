import json
import boto3
from botocore.config import Config
import os
import subprocess


def load_aws_credentials():
    try:
        return {
            "aws_access_key_id": os.environ["AWS_ACCESS_KEY_ID"],
            "aws_secret_access_key": os.environ["AWS_SECRET_ACCESS_KEY"],
            "region": os.getenv("AWS_REGION", "eu-central-1")
        }
    except KeyError as e:
        print(f"Missing AWS credential environment variable: {e}")
        return None
    

def configure_aws_cli(aws_creds):

    failed = 0

    commands = [
        ["aws", "configure", "set", "aws_access_key_id", aws_creds["aws_access_key_id"]],
        ["aws", "configure", "set", "aws_secret_access_key", aws_creds["aws_secret_access_key"]],
        ["aws", "configure", "set", "region", aws_creds.get("region", "us-west-2")],
    ]

    for cmd in commands:
        result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        if result.returncode != 0:
            failed = 1
            print(f"Error configuring AWS CLI: {result.stderr}")
    
    if failed == 0:
        print("Successful connection to AWS")
    

def AWS_Client():
    aws_creds = load_aws_credentials()
    s3_config = Config(signature_version='s3v4')

    s3_client = boto3.client(
    "s3",
    region_name="eu-central-1",
    aws_access_key_id=aws_creds["aws_access_key_id"],
    aws_secret_access_key=aws_creds["aws_secret_access_key"],
    config=s3_config
    )

    configure_aws_cli(aws_creds) # Testing connection to AWS Account

    return s3_client

