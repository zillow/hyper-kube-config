import os

import boto3

CLUSTER_TABLE = None
AWS_DEFAULT_REGION = os.environ.get('AWS_DEFAULT_REGION', 'us-west-2')


def get_cluster_table(cluster_table_name=None, region_name=AWS_DEFAULT_REGION):
    """
    Get the dynamodb cluster table.
    """
    global CLUSTER_TABLE
    dynamodb = boto3.resource('dynamodb', region_name=region_name)
    if cluster_table_name is None:
        cluster_table_name = os.environ['DYNAMODB_TABLE_K8_CLUSTERS']

    if CLUSTER_TABLE is None:
        CLUSTER_TABLE = dynamodb.Table(cluster_table_name)
    return CLUSTER_TABLE


def create_table(table_name, region_name=AWS_DEFAULT_REGION):
    dynamodb = boto3.resource('dynamodb', region_name=region_name)
    dynamodb.create_table(
        AttributeDefinitions=[
            {
                'AttributeName': 'id',
                'AttributeType': 'S'
            },
        ],
        TableName=table_name,
        KeySchema=[
            {
                'AttributeName': 'id',
                'KeyType': 'HASH'
            }
        ],
        ProvisionedThroughput={
            'ReadCapacityUnits': 1,
            'WriteCapacityUnits': 5
        },
    )
    return get_cluster_table(table_name)


def delete_table(table_name, region_name=AWS_DEFAULT_REGION):
    dynamodb = boto3.client('dynamodb', region_name=region_name)
    try:
        dynamodb.delete_table(TableName=table_name)
        deleted = True
    except dynamodb.exceptions.ResourceNotFoundException:
        deleted = False
    return deleted
