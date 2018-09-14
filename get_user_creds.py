import json
import os
import sys
sys.path.insert(0, './vendor-boto3')
import boto3
from util import validate_config_input, validate_unique_cluster_name

DYNAMODB = boto3.resource('dynamodb')
CLUSTER_TABLE_NAME = os.environ['DYNAMODB_TABLE_K8_CLUSTERS']
CLUSTER_TABLE = DYNAMODB.Table(CLUSTER_TABLE_NAME)
SECRETS_CLIENT = boto3.client('secretsmanager')

def get_user_creds(event, context):
    """Get user creds for a given user and cluster"""
    user = event['queryStringParameters']['user']
    cluster_name = event['queryStringParameters']['cluster_name']

    if validate_unique_cluster_name(cluster_name, CLUSTER_TABLE) is not None:

        cluster = CLUSTER_TABLE.get_item(Key={"id": cluster_name})

        if user in cluster['Item']['users']:
            print("User: {user} found. Retrieving creds...")
            user_secrets = get_secrets(user, cluster_name)

            return {
                "statusCode": 200,
                "body": json.dumps(user_secrets)
            }
        return {
            "statusCode": 404,
            "body": json.dumps(
                {"message": f'User: {user} not found for {cluster_name}'}
            )
        }

def get_secrets(user, cluster_name):
    """Get associated secrets"""
    
    user_secrets = ['user', 'user-client-key-data', 'user-client-certificate-data']
    user_secret_response = {}

    for user_secret in user_secrets:
        try: 
            response = SECRETS_CLIENT.get_secret_value(
                SecretId=f'{user_secret}-{user}-{cluster_name}'
            )
            if user_secret == "user":
                user_secret_response.update({user:response['SecretString']})
            elif user_secret == "user-client-key-data":
                user_secret_response.update({"client-key-data":response['SecretString']})
            elif user_secret == "client-certificate-data":
                user_secret_response.update({"client-certificate-data":response['SecretString']})
        except Exception as err:
            print(f"Secret {user_secret} not found, nothing to delete: {err}")
    
    return user_secret_response