import json
import os
import boto3
from util import validate_config_input, validate_unique_cluster_name

DYNAMODB = boto3.resource('dynamodb')
CLUSTER_TABLE_NAME = os.environ['DYNAMODB_TABLE_K8_CLUSTERS']
CLUSTER_TABLE = DYNAMODB.Table(CLUSTER_TABLE_NAME)
SECRETS_CLIENT = boto3.client('secretsmanager')


def add_cluster(event, context):
    """Add cluster and initial credentials. Handler function for lambda (entry point)"""
    
    validate_config_input(event['body'])
    cluster_config = json.loads(event['body'])
    cluster_users = cluster_config['users']

    for cluster in get_clusters(cluster_config):
        try:
            cluster_name = cluster['name']
            cluster_server = cluster['cluster']['server']
            cluster_authority = cluster['cluster']['certificate-authority-data']
        except KeyError as err:
            print(f'Invalid cluster config: {err}')
            raise err

        # Put into dynamodb cluster info
        if validate_unique_cluster_name(cluster_name, CLUSTER_TABLE) is None:
            names = [user['name'] for user in get_users(cluster_config)]

            for name in get_users(cluster_config):
                for user_data,secret in name['user'].items():
                    save_creds(cluster_name, name['name'], user_data, secret)
                    update_cluster_users_secret_name(cluster_name, name['name'], user_data, cluster_users)

            CLUSTER_TABLE.put_item(
                Item={
                    'id': cluster_name,
                    'server': cluster_server,
                    'certificate-authority-data': cluster_authority,
                    'users': [names],
                    'users_config': cluster_users
                }
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

def get_users(cluster_config):
    """Get users from config object"""

    users = [user for user in cluster_config['users']]
    return users

def save_creds(cluster_name, name, user_data, secret):
    """Save creds for users in config object"""

    print(f'Saving {name}-{user_data}-{cluster_name} secret...')
    SECRETS_CLIENT.create_secret(
        Name=f'{name}-{user_data}-{cluster_name}',
        SecretString=secret,
        Tags=[
            {
                'Key': 'cluster_name',
                'Value': cluster_name
            },
            {
                'Key': 'name',
                'Value': name
            },
            {
                'Key': 'user_data',
                'Value': user_data
            }
        ]
    )

def get_clusters(cluster_config):
    """Get list of clusters"""
    clusters = [cluster for cluster in cluster_config['clusters']]
    return clusters

def update_cluster_users_secret_name(cluster_name, name, user_data, cluster_users):
    """Update secret data with AWS Secret Manager reference name"""
    print(f'HERE is cluster_users: {cluster_users}')
    for user in cluster_users:
        if user['name'] == name and user_data in user['user']:
            user['user'][user_data] = f'{name}-{user_data}-{cluster_name}'
