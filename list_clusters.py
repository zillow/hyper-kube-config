import json
import os
import boto3

DYNAMODB = boto3.resource('dynamodb')
CLUSTER_TABLE_NAME = os.environ['DYNAMODB_TABLE_K8_CLUSTERS']
CLUSTER_TABLE = DYNAMODB.Table(CLUSTER_TABLE_NAME)


def list_clusters(event, context):
    """List clusters"""
    
    clusters = []
    cluster_items = CLUSTER_TABLE.scan()

    for cluster in cluster_items['Items']:
        clusters.append(cluster['id'])

    return {
        "statusCode": 200,
        "body": json.dumps(clusters)
    }