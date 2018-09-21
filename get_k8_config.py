import json
import os
import boto3
from util import validate_config_input, validate_unique_cluster_name

DYNAMODB = boto3.resource('dynamodb')
CLUSTER_TABLE_NAME = os.environ['DYNAMODB_TABLE_K8_CLUSTERS']
CLUSTER_TABLE = DYNAMODB.Table(CLUSTER_TABLE_NAME)
SECRETS_CLIENT = boto3.client('secretsmanager')

def get_k8_config(event, context):
    """Generate k8 config object from list of clusters as query input"""
    # /get_k8_configm?cloud-infra.cloud&cloud-infra-2.net
    clusters = event['queryStringParameters']
    config = {
        "apiVersion": "v1",
        "kind": "Config",
        "preferences": {},
        "clusters": [],
        "users": []
    }

    for cluster in clusters:
        if validate_unique_cluster_name(cluster, CLUSTER_TABLE) is not None:
            
            cluster_item = CLUSTER_TABLE.get_item(Key={"id": cluster})
            cluster_name = cluster

            config["clusters"].append(
                {"cluster": 
                    { "certificate-authority-data": cluster_item['certificate-authority-data'], 
                      "server": cluster_item['server']
                    }, 
                    "name": cluster_item['id']
                }
            )
            for user in cluster_item['users_config']['users']:
                for user_data in user:
                    for user_key,secret in user_data['user'].items():
                        secret = SECRETS_CLIENT.get_secret_value(
                            SecretId=f'{user_data["name"]}-{user_key}-{cluster_name}'
                        )

            config["users"].append(cluster_item['user_config']['users'])

            return {
                "statusCode": 200,
                "body": json.dumps(config)
            }
        return {
            "statusCode": 404,
            "body": json.dumps(
                {"message": f'Unable to process cluster config'}
            )
        }