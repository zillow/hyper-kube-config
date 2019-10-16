import json

import boto3

from botocore.exceptions import ClientError

SECRETS_CLIENT = boto3.client('secretsmanager')


def add_pem(event, context):
    """Add pem file and associate to a k8s cluster via a tag"""

    pem = event['body']
    cluster_name = event['queryStringParameters']['cluster_name']

    try:
        print(f'Adding hyper-kube-config-pem-{cluster_name}')
        SECRETS_CLIENT.create_secret(
            Name=f'hyper-kube-config-pem-{cluster_name}',
            SecretString=pem,
            Tags=[
                {
                    'Key': 'cluster_name',
                    'Value': cluster_name
                },
                {
                    'Key': 'pem',
                    'Value': "True"
                },
            ]
        )

        return {
            "statusCode": 200,
            "body": json.dumps(
                {"message": f'Pem added and associated to {cluster_name}'}
            ),
        }
    except ClientError as e:
        return {
            "statusCode": 503,
            "body": json.dumps(
                {"message":
                 f'Failed to add pem and associate to {cluster_name}: {e}'}
            )
        }


def get_pem(event, context):
    """Get the pem file for a specific cluster"""

    cluster_name = event['queryStringParameters']['cluster_name']

    try:
        print(f'Getting hyper-kube-config-pem-{cluster_name}')
        pem = SECRETS_CLIENT.get_secret_value(
            SecretId=f'hyper-kube-config-pem-{cluster_name}',
        )

        return {
            "statusCode": 200,
            "body": str(pem['SecretString']),
        }

    except ClientError as e:
        return {
            "statusCode": 503,
            "body": json.dumps(
                {"message":
                 f'Failed to get pem associated to {cluster_name}: {e}'}
            )
        }


def remove_pem(event, context):
    """Remove pem secret for a specific cluster"""

    cluster_name = event['queryStringParameters']['cluster_name']

    try:
        print(f'Deleting hyper-kube-config-pem-{cluster_name}')
        SECRETS_CLIENT.delete_secret(
            SecretId=f'hyper-kube-config-pem-{cluster_name}',
            ForceDeleteWithoutRecovery=True
        )

        return {
            "statusCode": 200,
            "body": {"message":
                     f'Deleted hyper-kube-config-pem-{cluster_name}'},
        }

    except ClientError as e:
        return {
            "statusCode": 503,
            "body": json.dumps(
                {"message": (f'Failed to get pem associated '
                             f'to {cluster_name}: {e}')}
            )
        }
