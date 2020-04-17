import decimal
import json


class DecimalEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, decimal.Decimal):
            return str(o)
        return super(DecimalEncoder, self).default(o)


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
    except Exception:
        # XXX - should catch the correct exceptions here.
        item = None
    return item


def lambda_result(data, status_code=200, **kwargs):
    if not isinstance(data, str):
        data = json.dumps(data, cls=DecimalEncoder)
    result = {
        "statusCode": status_code,
        "body": data
    }
    result.update(kwargs)
    return result
