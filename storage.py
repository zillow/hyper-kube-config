import os

import boto3


CLUSTER_TABLE = None


def get_cluster_table(cluster_table_name=None):
    """
    Get the dynamodb cluster table.
    """
    global CLUSTER_TABLE
    dynamodb = boto3.resource('dynamodb')
    if cluster_table_name is None:
        cluster_table_name = os.environ['DYNAMODB_TABLE_K8_CLUSTERS']

    if CLUSTER_TABLE is None:
        CLUSTER_TABLE = dynamodb.Table(cluster_table_name)
    return CLUSTER_TABLE


def create_table(table_name):
    dynamodb = boto3.resource('dynamodb')
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


def delete_table(table_name):
    dynamodb = boto3.client('dynamodb')
    dynamodb.delete_table(TableName=table_name)
