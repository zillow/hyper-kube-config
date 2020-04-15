import json
import logging
import os

from boto3.dynamodb.conditions import Key
# from boto3.dynamodb.types import TypeDeserializer

import storage


logger = logging.getLogger('cluster_status')
if os.environ.get('DEBUG'):
    logger.setLevel(logging.DEBUG)


def set_cluster_status(event, context):
    """Set the status of a cluster, ie active, inactive,
    maintainance_mode, etc"""

    CLUSTER_TABLE = storage.get_cluster_table()
    query_string_params = event.get('queryStringParameters', {})
    cluster_status = query_string_params.get('cluster_status')
    if cluster_status is None:
        return {
            "statusCode": 500,
            "body": {"message":
                     f'Must provide a status variable in uri query string'}
        }

    cluster_name = query_string_params.get('cluster_name')
    if cluster_name is None:
        return {
            "statusCode": 500,
            "body": {"message": (f'Must provide a cluster_name '
                                 f'variable in uri query string')}
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
            "body": {"message": (f'Updated cluster status for {cluster_name} '
                                 f'to {cluster_status}')}
        }
    except Exception:
        failed_txt = f'Failed to update cluster status for {cluster_name}'
        logger.exception(failed_txt)
        return {
            "statusCode": 500,
            "body": {"message": failed_txt}
        }


def set_cluster_environment(event, context):
    """Set the environment of a cluster, ie dev, stage, prod"""

    CLUSTER_TABLE = storage.get_cluster_table()
    query_string_params = event.get('queryStringParameters', {})
    environment = query_string_params.get('environment')
    if environment is None:
        return {
            "statusCode": 500,
            "body": {"message":
                     f'Must provide an environment param in uri query string'}
        }

    cluster_name = query_string_params.get('cluster_name')
    if cluster_name is None:
        return {
            "statusCode": 500,
            "body": {"message": (f'Must provide a cluster_name '
                                 f'variable in uri query string')}
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
        msg = (f'Updated cluster environment for {cluster_name} '
               f'to {environment}')
        return {
            "statusCode": 200,
            "body": {"message": msg}
        }
    except Exception:
        failed_txt = f'Failed to update cluster environment for {cluster_name}'
        print(failed_txt)
        return {
            "statusCode": 500,
            "body": {"message": failed_txt}
        }


def clusters_per_environment(event, context):
    """Query cluster status attribute for given environment,
    requires 'environment' query param, or defaults to all clusters"""

    clusters = []

    environment = event.get('queryStringParameters', {}).get('environment')

    items = _query_dynamodb(environment)

    for cluster in items:
        clusters.append(cluster['id'])

    return {
        "statusCode": 200,
        "body": json.dumps(clusters)
    }


def cluster_status(event, context):
    """Query cluster status attribute for given environment,
    requires 'environment' query param, or defaults to all clusters"""

    clusters = []
    query_string_params = event.get('queryStringParameters', {})
    environment = query_string_params.get('environment')
    cluster_status = query_string_params.get('cluster_status')

    items = _query_dynamodb(environment, cluster_status)

    for cluster in items:
        clusters.append(cluster['id'])

    return {
        "statusCode": 200,
        "body": json.dumps(clusters)
    }


def set_cluster_metadata(event, context):
    """Set the metadata of a cluster.
    metadata is a json blob use for describing extra details about a cluster.
    """

    CLUSTER_TABLE = storage.get_cluster_table()
    query_string_params = event.get('queryStringParameters', {})

    metadata = event.get('body', {})
    cluster_name = query_string_params.get('cluster_name')
    if cluster_name is None:
        return {
            "statusCode": 500,
            "body": {"message": (f'Must provide a cluster_name '
                                 f'variable in uri query string')}
        }

    try:
        if isinstance(metadata, str):
            metadata = json.loads(metadata)
        CLUSTER_TABLE.update_item(
            Key={
                'id': cluster_name,
            },
            UpdateExpression="set metadata = :md",
            ExpressionAttributeValues={
                ':md': metadata
            },
            ReturnValues="UPDATED_NEW"
        )
        return {
            "statusCode": 200,
            "body": {"message": f'Updated cluster metadata for {cluster_name}'}
        }
    except Exception:
        failed_txt = f'Failed to update cluster metadata for {cluster_name}'
        logger.exception(failed_txt)
        logger.error(json.dumps(event))
        return {
            "statusCode": 500,
            "body": {"message": failed_txt}
        }


def get_cluster_metadata(event, context):
    """Get the metadata of a cluster.
    metadata is a json blob use for describing extra details about a cluster.
    """

    CLUSTER_TABLE = storage.get_cluster_table()
    query_string_params = event.get('queryStringParameters', {})

    cluster_name = query_string_params.get('cluster_name')
    if cluster_name is None:
        return {
            "statusCode": 500,
            "body": {"message": (f'Must provide a cluster_name '
                                 f'variable in uri query string')}
        }
    status_code = 404
    db_response = CLUSTER_TABLE.get_item(
        Key={
            'id': cluster_name,
        }
    )
    metadata = {}
    if 'Item' in db_response:
        status_code = 200
        metadata = db_response['Item'].get('metadata', {})
        if isinstance(metadata, str):
            metadata = json.loads(metadata)
        metadata['environment'] = db_response['Item'].get('environment')
        metadata['status'] = db_response['Item'].get('status')
    metadata['id'] = cluster_name
    response = {'statusCode': status_code, "body": json.dumps(metadata)}

    return response


def _query_dynamodb(environment, status=None, metadata=False):
    CLUSTER_TABLE = storage.get_cluster_table()
    fkey = Key('environment').eq(environment)
    if status is not None:
        fkey = fkey & Key('cluster_status').eq(status)
    response = CLUSTER_TABLE.scan(
        ProjectionExpression="id",
        FilterExpression=fkey
    )
    return response.get('Items', [])
