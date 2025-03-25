import os
import json
import logging
from dotenv import load_dotenv
from azure.cosmos import CosmosClient
import boto3
from botocore.exceptions import NoCredentialsError

# ---------- Setup Logging ----------
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ---------- Load Env Variables ----------
load_dotenv()

COSMOS_CONNECTION_STRING = os.getenv("COSMOS_CONNECTION_STRING")
DATABASE_NAME = os.getenv("COSMOS_DATABASE", "cosmicworks")
CONTAINER_NAME = os.getenv("COSMOS_CONTAINER", "products")

AWS_REGION = "us-east-1"
S3_BUCKET_NAME = os.getenv("S3_BUCKET_NAME") 
S3_OBJECT_KEY = os.getenv("S3_OBJECT_KEY", "cosmos/cosmos_backup.json")  

# ---------- Initialize Cosmos Client ----------
cosmos_client = CosmosClient.from_connection_string(COSMOS_CONNECTION_STRING)
database = cosmos_client.get_database_client(DATABASE_NAME)
container = database.get_container_client(CONTAINER_NAME)

# ---------- Initialize S3 Client ----------
s3_client = boto3.client("s3", region_name=AWS_REGION)

def export_cosmos_data():
    logger.info(f"Exporting data from Cosmos DB: {DATABASE_NAME}/{CONTAINER_NAME}")
    items = list(container.read_all_items())
    logger.info(f"Fetched {len(items)} items from Cosmos DB.")
    return items

def upload_to_s3(data):
    try:
        json_data = json.dumps(data, indent=2)
        s3_client.put_object(Bucket=S3_BUCKET_NAME, Key=S3_OBJECT_KEY, Body=json_data)
        logger.info(f"Successfully uploaded data to s3://{S3_BUCKET_NAME}/{S3_OBJECT_KEY}")
    except NoCredentialsError:
        logger.error("AWS credentials not found. Please configure them sproperly.")

def main():
    items = export_cosmos_data()
    upload_to_s3(items)

if __name__ == "__main__":
    main()
