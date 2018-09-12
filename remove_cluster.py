import json
import os
import boto3
from util import validate_config_input, validate_unique_cluster_name

DYNAMODB = boto3.resource('dynamodb')
CLUSTER_TABLE_NAME = os.environ['DYNAMODB_TABLE_K8_CLUSTERS']
CLUSTER_TABLE = DYNAMODB.Table(CLUSTER_TABLE_NAME)
SECRETS_CLIENT = boto3.client('secretsmanager')


def remove_cluster(event, context):
    """Remove cluster and all associated credentials"""

    """{ "cluster_name": "foo-prod-cluster.com" }"""
    validate_config_input(event['body'])
    post_body = json.loads(event['body'])
    cluster_name = post_body['cluster_name']

    if validate_unique_cluster_name(cluster_name, CLUSTER_TABLE) is not None:

        cluster = CLUSTER_TABLE.get_item(Key={"id": cluster_name})

        # Remove associated user secrets
        for user in cluster['Item']['users']:
            delete_secrets(user, cluster_name)
        
        # Remove cluster
        CLUSTER_TABLE.delete_item(
            Key={
                'id': cluster_name
            }
        )

        return {
            "statusCode": 200,
            "body": json.dumps(
                {"message": f'Cluster and associated secrets removed for: {cluster_name}'}
            ),
        }
    return {
        "statusCode": 404,
        "body": json.dumps(
            {"message": f'Cluster {cluster_name} does not exist'}
        )
    }

def delete_secrets(user, cluster_name):
    """Delete secrets"""
    user_secrets = ['user', 'user-client-key-data', 'user-client-certificate-data']

    for secret in user_secrets:
        try: 
            SECRETS_CLIENT.delete_secret(
                SecretId=f'{secret}-{user}-{cluster_name}',
                ForceDeleteWithoutRecovery=True
            )
        except Exception as err:
            print(f"Secret {secret} not found, nothing to delete: {err}")
