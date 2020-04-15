import os
import unittest


from moto import mock_dynamodb2

import cluster_status


@mock_dynamodb2
class ClusterMetadataTestCase(unittest.TestCase):
    """Testing for add_cluster.py"""

    def setUp(self):
        self.table_name = "hyper-kube-config-test"
        self.cluster_name = 'test_cluster_name'
        os.environ["DYNAMODB_TABLE_K8_CLUSTERS"] = self.table_name
        # Delete just incase
        cluster_status.storage.delete_table(self.table_name)
        self.dbtable = cluster_status.storage.create_table(self.table_name)
        self.dbtable.put_item(
            Item={
                'id': self.cluster_name,
                'server': 'cluster.server.tld',
            }
        )

    def tearDown(self):
        os.environ["DYNAMODB_TABLE_K8_CLUSTERS"] = self.table_name
        cluster_status.storage.delete_table(self.table_name)

    def test_add_cluster_metadata(self):
        os.environ["DYNAMODB_TABLE_K8_CLUSTERS"] = self.table_name
        event = {'queryStringParameters':
                 {'cluster_name': 'test_cluster_name'},
                 'body': {'test_info': 'testing 1 2 3'}}
        cluster_status.set_cluster_metadata(event, {})

    def test_get_cluster_metadata(self):
        os.environ["DYNAMODB_TABLE_K8_CLUSTERS"] = self.table_name
        event = {'queryStringParameters':
                 {'cluster_name': 'test_cluster_name'},
                 'body': {'test_info': 'testing 1 2 3'}}
        res = cluster_status.set_cluster_metadata(event, {})
        self.assertEqual(200, res.get('statusCode'))
        metadata = cluster_status.get_cluster_metadata(event, {})
        self.assertEqual(200, metadata.get('statusCode'))
        self.assertIn('body', metadata)
        body = cluster_status.json.loads(metadata['body'])
        self.assertEqual('test_cluster_name', body.get('id'))
        self.assertIn('test_info', body)
        self.assertEqual('testing 1 2 3', body['test_info'])
