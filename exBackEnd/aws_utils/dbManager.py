import boto3
import os
from botocore.exceptions import NoCredentialsError
from aws_utils.awsManager import AWS_Client

ICONS = [
    "static/images/customEnvironmentIcons/door_blue.png",
    "static/images/customEnvironmentIcons/door_blue_u.png",
    "static/images/customEnvironmentIcons/door_green.png",
    "static/images/customEnvironmentIcons/door_green_u.png",
    "static/images/customEnvironmentIcons/door_grey.png",
    "static/images/customEnvironmentIcons/door_grey_u.png",
    "static/images/customEnvironmentIcons/door_purple.png",
    "static/images/customEnvironmentIcons/door_purple_u.png",
    "static/images/customEnvironmentIcons/door_red.png",
    "static/images/customEnvironmentIcons/door_red_u.png",
    "static/images/customEnvironmentIcons/door_yellow.png",
    "static/images/customEnvironmentIcons/door_yellow_u.png",
    "static/images/customEnvironmentIcons/goal.png",
    "static/images/customEnvironmentIcons/key_blue.png",
    "static/images/customEnvironmentIcons/key_green.png",
    "static/images/customEnvironmentIcons/key_grey.png",
    "static/images/customEnvironmentIcons/key_purple.png",
    "static/images/customEnvironmentIcons/key_red.png",
    "static/images/customEnvironmentIcons/key_yellow.png",
    "static/images/customEnvironmentIcons/lava.png",
    "static/images/customEnvironmentIcons/player.png"
]

IMAGES = [
    "static/images/gifs/UnlockEnv.gif",
    "static/images/gifs/CrossingEnv.gif",
    "static/images/gifs/DynamicObstaclesEnv.gif",
    "static/images/gifs/RedBlueDoorEnv.gif",
    "static/images/gifs/ObstructedMaze_1Dlhb.gif",
    "static/images/gifs/KeyCorridorEnv.gif",
    "static/images/gifs/GoToDoorEnv.gif",
    "static/images/gifs/DoorKeyEnv.gif",
    "static/images/gifs/BlockedUnlockPickupEnv.gif",
    "static/images/contactPage/Aisha.jpg",
    "static/images/contactPage/Ramiz.jpg",
    "static/images/contactPage/gmail.png"
]


def list_agents(bucket = "explainingai" , prefix = "storage/"):
    s3_client = boto3.client('s3')
    directories = set()

    try:
        response = s3_client.list_objects_v2(Bucket=bucket, Prefix=prefix, Delimiter='/')

        # Extract common prefixes (directories)
        if 'CommonPrefixes' in response:
            directories = [common_prefix['Prefix'].split('/')[-2] for common_prefix in response['CommonPrefixes']]

    except Exception as e:
        print(f"Error listing directories in S3: {str(e)}")

    return directories



def upload_agent(model_dir):
    """
    Upload all files from a local directory (model_dir) to S3, creating a
    "storage/<directory_name>" prefix where <directory_name> is the name of model_dir.

    Parameters:
    - model_dir: Path to the local directory containing model files.
    """
    model_dir = "storage/" + model_dir  # Ensure correct pat

    bucket_name = "explainingai"  # Replace with your actual S3 bucket name
    # Extract the last directory name (e.g., "Unlockenv" if model_dir ends with "/Unlockenv")
    directory_name = os.path.basename(os.path.normpath(model_dir))

    s3_prefix = f"storage/{directory_name}/"  # S3 prefix

    print("Prefix = " , s3_prefix)

    s3_client = boto3.client('s3')

    try:

        for root, dirs, files in os.walk(model_dir):
            for file in files:
                local_path = os.path.join(root, file)
                relative_path = os.path.relpath(local_path, model_dir)

                s3_key = os.path.join(s3_prefix, relative_path).replace("\\", "/")  # Ensure forward slashes for S3

                try:

                    s3_client.upload_file(local_path, bucket_name, s3_key)
                    print(f"Uploaded {local_path} to s3://{bucket_name}/{s3_key}")
                except Exception as e:

                    print("No valid AWS credentials found. Exiting.")

                    raise SystemExit("Exiting due to missing credentials") from e
                except Exception as e:
                    print(f"Error uploading {local_path} to s3://{bucket_name}/{s3_key}: {str(e)}")
                    raise

        print(f"All files from {model_dir} have been uploaded to s3://{bucket_name}/{s3_prefix}")

    except Exception as e:
        print(f"Error walking the directory {model_dir}: {str(e)}")
        raise




def get_storage_dir():
    """
    Get the local directory for storing models downloaded from S3.
    """
    return os.path.join(os.getcwd(), "storage") 

def download_file_from_s3(bucket_name, s3_key, local_path):
    """
    Download a single file from S3 and save it locally.

    Parameters:
    - bucket_name: The S3 bucket name.
    - s3_key: The key (path) of the file in S3.
    - local_path: The local path to save the file.
    """
    s3_client = boto3.client('s3')
    try:
        os.makedirs(os.path.dirname(local_path), exist_ok=True)  # Ensure local directory exists
        s3_client.download_file(bucket_name, s3_key, local_path)  # Download file
        print(f"Downloaded {s3_key} from {bucket_name} to {local_path}")
    except NoCredentialsError:
        print("AWS credentials not available.")
        raise
    except Exception as e:
        print(f"Error downloading {s3_key} from S3: {str(e)}")
        raise

def download_agent(directory_name):
    """
    Download all files from the specified S3 directory (prefix) and save them locally.

    Parameters:
    - directory_name: The name of the S3 directory (prefix) to download (e.g., 'Unlockenv').

    Returns:
    - The local directory where files are saved.
    """
    bucket_name = "explainingai"  # Replace with your actual S3 bucket name
    s3_prefix = f"storage/{directory_name}/"  # The S3 prefix (directory)
    local_dir = os.path.join(get_storage_dir(), directory_name)

    s3_client = boto3.client('s3')

    try:
        
        response = s3_client.list_objects_v2(Bucket=bucket_name, Prefix=s3_prefix)

        if 'Contents' not in response:
            print(f"No files found in {s3_prefix}. Check if the path exists in S3.")
            return None

        for obj in response['Contents']:
            s3_key = obj['Key']  # Full path in S3
            relative_path = s3_key[len(s3_prefix):]  # Get relative file path
            local_file_path = os.path.join(local_dir, relative_path)  # Local storage path

            if relative_path:  # Skip empty keys (folders in S3)
                download_file_from_s3(bucket_name, s3_key, local_file_path)

        print(f"All files downloaded to {local_dir}")
        return local_dir

    except Exception as e:
        print(f"Error fetching file list from S3: {str(e)}")
        raise


def fetch_ImageURLS():

    signed_urls = []

    s3_client = AWS_Client()

    for image in IMAGES:

        signed_url = s3_client.generate_presigned_url(
        "get_object",
        Params={"Bucket": "explainingai", "Key": image},
        ExpiresIn=3600  # Link valid for 1 hour
        )
        signed_urls.append(signed_url)
    return signed_urls

def fetch_IconURLS():

    signed_icons = []

    s3_client = AWS_Client()

    for icon in ICONS:
        signed_url = s3_client.generate_presigned_url(
            "get_object",
            Params={"Bucket": "explainingai", "Key": icon},
            ExpiresIn=3600  # Link valid for 1 hour
        )
        signed_icons.append(signed_url)

    return signed_icons