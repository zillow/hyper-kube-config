import json
import os
import boto3
from util import validate_config_input, validate_unique_cluster_name

DYNAMODB = boto3.resource('dynamodb')
CLUSTER_TABLE_NAME = os.environ['DYNAMODB_TABLE_K8_CLUSTERS']
CLUSTER_TABLE = DYNAMODB.Table(CLUSTER_TABLE_NAME)
SECRETS_CLIENT = boto3.client('secretsmanager')

def add_cluster(event, context):
    """Add cluster and initial credentials"""

    validate_config_input(event['body'])
    cluster_config = json.loads(event['body'])

    try:
        cluster_name = cluster_config['clusters'][0]['name']
        cluster_server = cluster_config['clusters'][0]['cluster']['server']
    except KeyError as err:
        print(f'Invalid cluster config: {err}')

        raise err
    # Put into dynamodb cluster info

    if validate_unique_cluster_name(cluster_name, CLUSTER_TABLE) is None:
        user_name = cluster_config['users'][0]['user']['username']
        password  = cluster_config['users'][0]['user']['password']
        user_client_key = cluster_config['users'][0]['user']['client-key-data']
        user_client_certificate_data = cluster_config['users'][0]['user']['client-certificate-data']
        CLUSTER_TABLE.put_item(
            Item={
                'id': cluster_name,
                'server': cluster_server,
                'users': [user_name] 
            }
        )

        # Put into secrets manager
        SECRETS_CLIENT.create_secret(
            Name=f'user-{user_name}-{cluster_name}',
            SecretString=password
        )

        SECRETS_CLIENT.create_secret(
            Name=f'user-client-key-data-{user_name}-{cluster_name}',
            SecretString=user_client_key
        )

        SECRETS_CLIENT.create_secret(
            Name=f'user-client-certificate-data-{user_name}-{cluster_name}',
            SecretString=user_client_certificate_data
        )

        return {
            "statusCode": 200,
            "body": json.dumps(
                {"message": f'Cluster and config added {cluster_name}'}
            ),
        }
    return {
        "statusCode": 404,
        "body": json.dumps(
            {"message": f'Cluster {cluster_name} already exists'}
        )
    }
