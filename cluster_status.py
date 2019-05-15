import json
import os
import boto3
from boto3.dynamodb.conditions import Key, Attr
from botocore.exceptions import ClientError


DYNAMODB = boto3.resource('dynamodb')
CLUSTER_TABLE_NAME = os.environ['DYNAMODB_TABLE_K8_CLUSTERS']
CLUSTER_TABLE = DYNAMODB.Table(CLUSTER_TABLE_NAME)


def set_cluster_status(event, context):
    """Set the status of a cluster, ie active, inactive, maintainance_mode, etc"""

    try:
        cluster_status = event['queryStringParameters']['cluster_status']
    except:
        return {
            "statusCode": 500,
            "body": {"message": f'Must provide a status variable in uri query string'}
        }
    try:
        cluster_name = event['queryStringParameters']['cluster_name']
    except:
        return {
            "statusCode": 500,
            "body": {"message": f'Must provide a cluster_name variable in uri query string'}
        }

    try:
        CLUSTER_TABLE.update_item(
            Key={
                'id': cluster_name,
            },
            UpdateExpression="set cluster_status = :r",
            ExpressionAttributeValues={
                ':r': cluster_status
            },
            ReturnValues="UPDATED_NEW"
        )
        return {
            "statusCode": 200,
            "body": {"message": f'Updated cluster status for {cluster_name} to {cluster_status}'}
        }
    except:
        print(f'Falied to update cluster status for {cluster_name}')
        return {
            "statusCode": 500,
            "body": {"message": f'Falied to update cluster status for {cluster_name}'}
        }


def set_cluster_environment(event, context):
    """Set the environment of a cluster, ie dev, stage, prod"""

    try:
        environment = event['queryStringParameters']['environment']
    except:
        return {
            "statusCode": 500,
            "body": {"message": f'Must provide an environment variable in uri query string'}
        }
    try:
        cluster_name = event['queryStringParameters']['cluster_name']
    except:
        return {
            "statusCode": 500,
            "body": {"message": f'Must provide a cluster_name variable in uri query string'}
        }

    try:
        CLUSTER_TABLE.update_item(
            Key={
                'id': cluster_name,
            },
            UpdateExpression="set environment = :e",
            ExpressionAttributeValues={
                ':e': environment
            },
            ReturnValues="UPDATED_NEW"
        )
        return {
            "statusCode": 200,
            "body": {"message": f'Updated cluster environment for {cluster_name} to {environment}'}
        }
    except:
        print(f'Falied to update cluster environment for {cluster_name}')
        return {
            "statusCode": 500,
            "body": {"message": f'Falied to update cluster environment for {cluster_name}'}
        }


def clusters_per_environment(event, context):
    """Query cluster status attribute for given environment, requires 'environment' query param, or defaults to all clusters"""

    environment = None
    clusters = []
    
    if event['queryStringParameters']['environment']:
        environment = event['queryStringParameters']['environment']

    items = _query_dynamodb_per_environment(environment)
    
    for cluster in items['Items']:
        clusters.append(cluster['id'])

    return {
        "statusCode": 200,
        "body": json.dumps(clusters)
    }


def cluster_status(event, context):
    """Query cluster status attribute for given environment, requires 'environment' query param, or defaults to all clusters"""

    environment = None
    cluster_status = None
    clusters = []
    
    if event['queryStringParameters']['environment']:
        environment = event['queryStringParameters']['environment']
    
    if event['queryStringParameters']['cluster_status']:
        cluster_status = event['queryStringParameters']['cluster_status']

    items = _query_dynamodb_per_environment_and_status(environment, cluster_status)

    for cluster in items:
        clusters.append(cluster['id'])

    return {
        "statusCode": 200,
        "body": json.dumps(clusters)
    }


def _query_dynamodb_per_environment_and_status(environment, status):
    response = CLUSTER_TABLE.scan(
        ProjectionExpression="id",
        FilterExpression=Key('environment').eq(environment) & Key('cluster_status').eq(status)
    )

    return response['Items']

def _query_dynamodb_per_environment(environment):
    response = CLUSTER_TABLE.scan(
        ProjectionExpression="id",
        FilterExpression=Key('environment').eq(environment)
    )

    return response['Items']
