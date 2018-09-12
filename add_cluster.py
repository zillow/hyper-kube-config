import boto3
import json
import os

dynamodb = boto3.resource('dynamodb')
cluster_table_name = os.environ['DYNAMODB_TABLE_K8_CLUSTERS']
cluster_table = dynamodb.Table(cluster_table_name)
secrets_client = boto3.client('secretsmanager')


def add_cluster(event, context):
    validate_config_input(event['body'])
    cluster_config = json.loads(event['body'])

    try:
        cluster_name = cluster_config['clusters'][0]['name']
        cluster_server = cluster_config['clusters'][0]['cluster']['server']
        
    except KeyError as e:
        print(f'Invalid cluster config: {e}')

        raise e
    # Put into dynamodb cluster info

    if validate_unique_cluster_name(cluster_table_name, cluster_name) == None:
        cluster_table.put_item(
            Item={
                'id': cluster_name,
                'server': cluster_server
            }
        )
        # Put into secrets manager
        user_name = cluster_config['users'][0]['user']['username'] 
        password  = cluster_config['users'][0]['user']['password'] 
        user_client_key = cluster_config['users'][0]['user']['client-key-data']
        user_client_certificate_data = cluster_config['users'][0]['user']['client-certificate-data']

        secrets_client.create_secret(
            Name=f'user-{user_name}-{cluster_name}',
            SecretString=password
        )
        
        secrets_client.create_secret(
            Name=f'user-client-key-{user_name}-{cluster_name}',
            SecretString=user_client_key
        )
        
        secrets_client.create_secret(
            Name=f'user-client-certificate-data-{user_name}-{cluster_name}',
            SecretString=user_client_certificate_data
        )

        return {
            "statusCode": 200,
            "body": json.dumps(
                {"message": f'Cluster and config added {cluster_name}'}
            ),
        }
    else:
        return {
            "statusCode": 404,
            "body": json.dumps(
                {"message": f'Cluster {cluster_name} already exists'}
            )
        }


def validate_config_input(config):
    try:
        json.loads(config)
    except ValueError as err:
        print(f'K8s config is not valid json error: {err}')

def validate_unique_cluster_name(cluster_table_name, cluster_name):
    try:
        item = cluster_table.get_item(Key={"id": cluster_name})
        print(f"Cluster {cluster_name} already exists: {item['Item']}")
    except:
        print(f'Cluster {cluster_name} not found')
        item = None
    return item