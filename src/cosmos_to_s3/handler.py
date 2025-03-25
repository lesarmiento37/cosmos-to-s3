import os
import json
import logging
from azure.cosmos import CosmosClient
import boto3
from botocore.exceptions import NoCredentialsError

# Setup Logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)

# Environment Variables (set these in Lambda console or with Terraform/CDK)
COSMOS_CONNECTION_STRING = os.getenv("COSMOS_CONNECTION_STRING")
DATABASE_NAME = os.getenv("COSMOS_DATABASE", "cosmicworks")
CONTAINER_NAME = os.getenv("COSMOS_CONTAINER", "products")

AWS_REGION = os.getenv("AWS_REGION", "us-east-1")
S3_BUCKET_NAME = os.getenv("S3_BUCKET_NAME")
S3_OBJECT_KEY = "cosmos/cosmos_backup.json"

# Initialize S3 Client
s3_client = boto3.client("s3", region_name=AWS_REGION)

def main(event, context):
    try:
        logger.info("Starting export from Cosmos DB to S3.")

        # Cosmos DB Client
        cosmos_client = CosmosClient.from_connection_string(COSMOS_CONNECTION_STRING)
        database = cosmos_client.get_database_client(DATABASE_NAME)
        container = database.get_container_client(CONTAINER_NAME)

        # Read items
        items = list(container.read_all_items())
        logger.info(f"Fetched {len(items)} items from Cosmos DB.")

        # Upload to S3
        json_data = json.dumps(items, indent=2)
        s3_client.put_object(Bucket=S3_BUCKET_NAME, Key=S3_OBJECT_KEY, Body=json_data)
        logger.info(f"Data uploaded to s3://{S3_BUCKET_NAME}/{S3_OBJECT_KEY}")

        return {
            "statusCode": 200,
            "body": f"Exported {len(items)} items to S3."
        }

    except NoCredentialsError:
        logger.error("Missing AWS credentials.")
        return {"statusCode": 500, "body": "AWS credentials missing."}
    except Exception as e:
        logger.exception("Error occurred during export.")
        return {"statusCode": 500, "body": str(e)}
