import json

import boto3
from botocore.exceptions import ClientError

from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives.serialization import load_pem_private_key
from cryptography.exceptions import UnsupportedAlgorithm


SECRETS_CLIENT = boto3.client('secretsmanager')


def add_ca_key(event, context):
    """Add and associate a K8s cluster's CA key, except key in pem format"""

    """
    "body":
    {
    "cluster_name": "cloud-infra.cloud",
    "ca_key": "'-----BEGIN RSA PRIVATE KEY-----\n
                PUT REAL KEY HERE
                \n-----END RSA PRIVATE KEY-----\n'"
    }
    """
    cluster_name = event['body']['cluster_name']

    # Load CA key from event body
    try:
        ca_key = str.encode(event['body']['ca_key'])
    except AttributeError:
        print(
            f'Error encoding {event["body"]["ca_key"]} must be string format')

    # Validate key by loading it in cryptography lib
    try:
        validate_key = load_pem_private_key(ca_key,
                                            password=None,
                                            backend=default_backend())
        print(f'Key validated with size: {validate_key.key_size}')
    except ValueError as err:
        print(f'ValueError: {err}')
    except TypeError as err:
        print(f'TypeError: {err}')
    except UnsupportedAlgorithm as err:
        print(f'UnsupportedAlgorithm: {err}')

    print(f'Saving hyper-kube-config-{cluster_name}-ca-key...')
    try:
        SECRETS_CLIENT.create_secret(
            Name=f'hyper-kube-config-{cluster_name}-ca-key',
            SecretString=ca_key,
            Tags=[
                {
                    'Key': 'cluster_name',
                    'Value': cluster_name
                }
            ]
        )
    except ClientError as err:
        if err.response['Error']['Code'] == 'EntityAlreadyExists':
            print(f'CA key already exists in AWS Secrets Manager: {err}')


def remove_ca_key(event, context):
    """Remove specified CA key"""

    cluster_name = event['body']['cluster_name']

    try:
        msg = f'Deleted hyper-kube-config-{cluster_name}-ca-key'
        print(msg)
        SECRETS_CLIENT.delete_secret(
            SecretId=f'hyper-kube-config-{cluster_name}-ca-key',
            ForceDeleteWithoutRecovery=True
        )

        return {
            "statusCode": 200,
            "body": {"message": msg}
        }

    except ClientError as e:
        err_msg = f'Failed to get ca key associated to {cluster_name}: {e}'
        return {
            "statusCode": 503,
            "body": json.dumps(
                {"message": err_msg}
            )
        }
