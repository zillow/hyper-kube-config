import json
import os
import boto3
from util import validate_config_input, validate_unique_cluster_name

DYNAMODB = boto3.resource('dynamodb')
CLUSTER_TABLE_NAME = os.environ['DYNAMODB_TABLE_K8_CLUSTERS']
CLUSTER_TABLE = DYNAMODB.Table(CLUSTER_TABLE_NAME)
SECRETS_CLIENT = boto3.client('secretsmanager')

config = {
    "apiVersion": "v1",
    "kind": "Config",
    "preferences": {},
    "clusters": [],
    "users": [],
    "contexts": [],
    "current-context": ""
}

def get_all_k8_configs(event, context):
    """Generate k8 config object for all tracked clusters"""

    # /get_all_k8s_configs
    clusters = _cluster_list()
    _generate_cluster_config(clusters)


def get_k8_config(event, context):
    """Generate k8 config object from list of clusters as query input"""
    
    # /get_k8_config?cloud-infra.cloud&cloud-infra-2.net
    clusters = event['queryStringParameters']
    _generate_cluster_config(clusters)


def _generate_cluster_config(clusters):
    for cluster in clusters:
        
        if validate_unique_cluster_name(cluster, CLUSTER_TABLE) is not None:

            cluster_item = CLUSTER_TABLE.get_item(Key={"id": cluster})
            cluster_item = cluster_item['Item']
            
            config["clusters"].append(
                {"cluster": 
                    { "certificate-authority-data": cluster_item['certificate-authority-data'], 
                      "server": cluster_item['server']
                    }, 
                    "name": cluster_item['id']
                }
            )

            for user in cluster_item['users_config']:
                for user_key, secret in user['user'].items():
                    secret_response = SECRETS_CLIENT.get_secret_value(
                        SecretId=secret
                    ) 
                    user['user'][user_key] = secret_response['SecretString'] 

            for user in cluster_item['users_config']:
                config["users"].append(user)

            config["contexts"].append(
                {"context": 
                    { "cluster": cluster_item['id'],
                      "user": cluster_item['id']
                    },
                    "name": cluster_item['id']
                }
            )

            # Last item processed will become the current-context in response
            config["current-context"] = cluster_item['id']

        else:
            return {
                "statusCode": 404,
                "body": json.dumps(
                    {"message": f'Unable to process cluster config for {cluster}, confirm cluster is in list endpoint output'}
                )
            }
    return {
        "statusCode": 200,
        "body": json.dumps(config)
    }

def _cluster_list():
    """Scan for all cluster ids and return list"""

    clusters = []
    cluster_items = CLUSTER_TABLE.scan()

    for cluster in cluster_items['Items']:
        clusters.append(cluster['id'])
    
    return clusters
