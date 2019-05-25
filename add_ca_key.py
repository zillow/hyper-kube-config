import json
import os
import boto3
from botocore.exceptions import ClientError
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives.serialization import load_pem_private_key
from cryptography.exceptions import UnsupportedAlgorithm
from util import validate_config_input, validate_unique_cluster_name

SECRETS_CLIENT = boto3.client('secretsmanager')


def add_ca_key(event, context):
    """Add and associate a K8s cluster's CA key, except key in pem format"""

    """ 
    "body": 
    {
    "cluster_name": "cloud-infra.cloud",
    "ca_key": "'-----BEGIN RSA PRIVATE KEY-----\n4AAF9F4AD236\n\nXwmQ3VLpDtZmcLdmmtVw8jJ0DX03xMJgoWru8t9TbrHwC+e9onlGO6v/PTOndLKT\nkN64ztLPZpawcr35LkgzETQA31kmaBvr8vmN4Y9OlXhjIZLJ7bBcAuJ9DR8V9Wnl\n0T+Ltjdj1QzdmXX0dB+8RH8t10gf/NQeIDz6KwXNGi1mehcW/VrcCDG0nE2IhQx4\nglA4rJoQZSrVp0Vq/5jL59MqlGMoD3rC5I9EvBV8kWFT92m7tcMNJP36RbvC/wyo\n2uHhyTh+vv9AYme+km0GHA+v+tm6wYJbZGpewYRLXX1PNMSVPCJs5hlnEVs3pOwP\nhags0ED9rO8xnLDQoIhZauOyN9ssFuKHTthruueg8abBoB1+tcptHpkbDPdU+uuK\n+UK//CHhIaUPXNkODuh30Drs1xQBHDSUtaDRfYszu3KpVw7AWjdXfAj8FsmKbPLz\nJWcAL9clj8yGd1Xxv58zvjUY8ysvXpLuNs15JB8lOlvYs3wE5tGOR0DgqWRxrlYw\nzKID0FUeUpF/sFNfiv2LQAqNzYb5DuMVkLDf11Xs4mUDa2lh3Ta40MKPWIuI5o0n\nLy/Bw5zNqJPpAHn9Q3CzZwwi129l30P/1PPxzhZfeW0Pk35EUaNVfls/tWqmqLj3\neFkaJ8i8CmSBDmAWTf47B0dfgTOe1CU1wSp/1/93x4rjLreYXKAuQVd6VKhbm6WQ\nuIaKdkql4vtdygS6oxGyzXJATi4wYmh2N6Rc6Q1WmO99bAwbpzE/WC2X+34j1jY7\nRN6e3KMTk5yKuVb/TfYUiJFyRJG2AFRtv48tHUk5g5XR2jJ/UPBeQrbgUu6jti6K\nZa7VGjJN0b+Xdjh3vN187gxCNpdj1DIc1EQ1PrpmSDNGoIrtqXOmE75t5e9YyLK0\n7KGl/t5rH2f+M3a3TSWi/F/RWBhS0nVa5GYWD9OREctXdJ3BjG0Xc8jUXs9/pWpV\nJUX8tPUKpYwE9Kgx/Tgq32zVGreDd2Jy+5qewX26MQYFtTVjJuj/kPo9KBWN39RT\nz4mEhX6M2qUfxoNtDO8vJuMIBSgbHs0hmAfBWl1dLxux5Tfh/lwcwA0v4UG1fQXn\nTK+ILpyM8SapUMLsFXSqQaZSfOj7mnrccy94ryW5Hr5PoarVMlWJXRoaLUy8dJfQ\ntdxBOMgpc4FjDNLABn3Y9StCPLVzSYosb2WeT+9m/7gIhn+mf49/7K4Q+cRqNh31\nN/DQ9Agx1eWWtBLUZ5FpIzccnbXxQG3KPRPGSbFVipILrR/yvoixc1jVzLarVIqs\nrQ9+tWSA5uZQknKoQ7gIv+BtT6S2onUd/tV1PsKFnZVgbSlp45QO2uq9wsJ5UvHq\nnAm8tPCU1LQwgIhdn6cPLe3Y6YvmpUHVi7mJD4nhwXkJKYifJk+pSbECudWpBTOe\n9bkyg2+VWNpiVAX9g/Nr5TiSYRfnRA245LFRLbOMkjMJr5Bd32KSc34fW1j0FJSG\n9wmRHt0VqrH7j3wmTsk9Cv/8ZzO0dzfjJng8S/BzuOuLcPHdchcCxbkPBFmPL33f\nnr3GEf46NIDqSTyOXyht3mhpRv1o2Ow6mS7NjL34sHCfz7rnCeuHy9m2OGBeI5uR\n-----END RSA PRIVATE KEY-----\n'"
    }
    """
    cluster_name = event['body']['cluster_name']

    # Load CA key from event body
    try:
        ca_key = str.encode(event['body']['ca_key'])
    except AttributeError:
        print(f'Error encoding {event["body"]["ca_key"]} must be string format')

    # Validate key by loading it in cryptography lib
    try:
        validate_key = load_pem_private_key(ca_key, password=None, backend=default_backend())
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