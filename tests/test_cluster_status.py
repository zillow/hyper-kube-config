import os
import unittest


from moto import mock_dynamodb2

import cluster_status


@mock_dynamodb2
class TestAddCluster(unittest.TestCase):
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

    def test_add_cluster_status(self):
        os.environ["DYNAMODB_TABLE_K8_CLUSTERS"] = self.table_name
        event = {'queryStringParameters':
                 {'cluster_status': 'testing',
                  'cluster_name': 'test_cluster_name'}}
        cluster_status.set_cluster_status(event, {})

    def test_get_cluster_status_not_found(self):
        os.environ["DYNAMODB_TABLE_K8_CLUSTERS"] = self.table_name
        event = {'queryStringParameters':
                 {'cluster_status': 'testing',
                  'cluster_name': 'test_cluster_name'}}
        res = cluster_status.set_cluster_status(event, {})
        self.assertEqual(200, res.get('statusCode'))
        event = {'queryStringParameters':
                 {'cluster_name': 'test_cluster_name'}}
        status = cluster_status.cluster_status(event, {})
        self.assertEqual(200, status.get('statusCode'))
        self.assertEqual('[]', status.get('body'))

    def test_get_cluster_status(self):
        os.environ["DYNAMODB_TABLE_K8_CLUSTERS"] = self.table_name
        event = {'queryStringParameters':
                 {'cluster_status': 'testing',
                  'environment': 'test',
                  'cluster_name': 'test_cluster_name'}}
        res = cluster_status.set_cluster_status(event, {})
        self.assertEqual(200, res.get('statusCode'))
        res = cluster_status.set_cluster_environment(event, {})
        self.assertEqual(200, res.get('statusCode'))
        event = {'queryStringParameters':
                 {'environment': 'test'}}
        status = cluster_status.cluster_status(event, {})
        self.assertEqual(200, status.get('statusCode'))
        self.assertEqual('["test_cluster_name"]', status.get('body'))

    def test_list_clusters_per_environment(self):
        os.environ["DYNAMODB_TABLE_K8_CLUSTERS"] = self.table_name
        event = {'queryStringParameters':
                 {'cluster_status': 'testing',
                  'environment': 'test',
                  'cluster_name': 'test_cluster_name'}}
        res = cluster_status.set_cluster_status(event, {})
        self.assertEqual(200, res.get('statusCode'))
        res = cluster_status.set_cluster_environment(event, {})
        self.assertEqual(200, res.get('statusCode'))
        event = {'queryStringParameters':
                 {'environment': 'test'}}
        status = cluster_status.clusters_per_environment(event, {})
        self.assertEqual(200, status.get('statusCode'))
        self.assertEqual('["test_cluster_name"]', status.get('body'))
        event = {'queryStringParameters':
                 {'environment': 'thisiswrong'}}
        status = cluster_status.clusters_per_environment(event, {})
        self.assertEqual(200, status.get('statusCode'))
        self.assertEqual('[]', status.get('body'))
