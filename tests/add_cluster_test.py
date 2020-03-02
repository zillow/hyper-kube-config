import unittest
import os

from moto import mock_dynamodb2

import add_cluster


@mock_dynamodb2
class TestAddCluster(unittest.TestCase):
    """Testing for add_cluster.py"""

    def setUp(self):
        self.table_name = "hyper-kube-config-test"
        self.cluster_name = 'test_cluster_name'
        os.environ["DYNAMODB_TABLE_K8_CLUSTERS"] = self.table_name
        self.dbtable = add_cluster.storage.create_table(self.table_name)
        self.dbtable.put_item(
            Item={
                'id': self.cluster_name,
                'server': 'cluster.server.tld',
            }
        )

    def tearDown(self):
        os.environ["DYNAMODB_TABLE_K8_CLUSTERS"] = self.table_name
        add_cluster.storage.delete_table(self.table_name)


if __name__ == '__main__':
    unittest.main()
