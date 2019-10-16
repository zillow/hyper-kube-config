import unittest
import os

import boto3

from moto import mock_dynamodb2

# XXX - should add a test!
# import add_cluster


class TestAddCluster(unittest.TestCase):
    """Testing for add_cluster.py"""

    @mock_dynamodb2
    def test_add_cluster(self):
        """Setup DynamoDB tables for hyper-kube-config
        """

        os.environ["DYNAMODB_TABLE_K8_CLUSTERS"] = "hyper-kube-config-test"
        self.dynamodb = boto3.resource('dynamodb', region_name='us-east-1')
        self.dynamodb.create_table(
            AttributeDefinitions=[
                {
                    'AttributeName': 'id',
                    'AttributeType': 'S'
                },
            ],
            TableName='hyper-kube-config-test',
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
        self.hyper_kube_config_table = self.dynamodb.Table(
            os.environ["DYNAMODB_TABLE_K8_CLUSTERS"])


if __name__ == '__main__':
    unittest.main()
