import json


def validate_config_input(config):
    """Validate config input is JSON"""
    try:
        json.loads(config)
    except ValueError as err:
        print(f'K8s config is not valid json error: {err}')

def validate_unique_cluster_name(cluster_name, cluster_table):
    """Validate cluster is a unique name"""
    try:
        item = cluster_table.get_item(Key={"id": cluster_name})
        print(f"Cluster {cluster_name} exists: {item['Item']}")
    except:
        print(f'Cluster {cluster_name} not found')
        item = None
    return item