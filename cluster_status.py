import json

from boto3.dynamodb.conditions import Key


import storage


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
        print(failed_txt)
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


def _query_dynamodb(environment, status=None):
    CLUSTER_TABLE = storage.get_cluster_table()
    fkey = Key('environment').eq(environment)
    if status is not None:
        fkey = fkey & Key('cluster_status').eq(status)
    response = CLUSTER_TABLE.scan(
        ProjectionExpression="id",
        FilterExpression=fkey
    )
    return response.get('Items', [])
