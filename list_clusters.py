import json

import storage


def list_clusters(event, context):
    """List clusters"""

    clusters = []
    cluster_items = storage.get_cluster_table().scan()

    for cluster in cluster_items.get('Items', []):
        clusters.append(cluster['id'])

    return {
        "statusCode": 200,
        "body": json.dumps(clusters)
    }
