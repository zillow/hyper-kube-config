import json
import os
import boto3
from util import validate_config_input, validate_unique_cluster_name

DYNAMODB = boto3.resource('dynamodb')
CLUSTER_TABLE_NAME = os.environ['DYNAMODB_TABLE_K8_CLUSTERS']
CLUSTER_TABLE = DYNAMODB.Table(CLUSTER_TABLE_NAME)
SECRETS_CLIENT = boto3.client('secretsmanager')


def remove_cluster(event, context):
    """Remove cluster and all associated credentials"""
    """{ "cluster_name": "foo-prod-cluster.com" }"""

    validate_config_input(event['body'])
    post_body = json.loads(event['body'])
    cluster_name = post_body['cluster_name']

    if validate_unique_cluster_name(cluster_name, CLUSTER_TABLE) is not None:

        # Remove associated user secrets
        delete_secrets(cluster_name)

        # Remove cluster
        CLUSTER_TABLE.delete_item(
            Key={
                'id': cluster_name
            }
        )

        return {
            "statusCode": 200,
            "body": json.dumps(
                {"message": (f'Cluster and associated secrets '
                             f'removed for: {cluster_name}')}
            ),
        }
    return {
        "statusCode": 404,
        "body": json.dumps(
            {"message": f'Cluster {cluster_name} does not exist'}
        )
    }


def delete_secrets(cluster_name):
    """Delete AWS Secrets Manager secrets"""

    resp = SECRETS_CLIENT.list_secrets()
    secrets = []
    while resp:
        secrets += resp['SecretList']
        nextToken = resp.get('NextToken')
        if nextToken is not None:
            resp = SECRETS_CLIENT.list_secrets(NextToken=nextToken)
        else:
            resp = None

    for secret in secrets:
        if 'Tags' in secret:
            for tag in secret['Tags']:
                if (tag['Key'] == 'cluster_name'
                   and tag['Value'] == cluster_name):
                    try:
                        print(f"Deleting secret: {secret['Name']}")
                        SECRETS_CLIENT.delete_secret(
                            SecretId=f"{secret['Name']}",
                            ForceDeleteWithoutRecovery=True
                        )
                    except Exception as err:
                        # XXX - handle correct exceptions here!
                        print((f"Secret {secret} not found, "
                               f"nothing to delete: {err}"))
