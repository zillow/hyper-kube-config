import json

def post_cluster(event, context):
    validate_config_input(event['body'])
    cluster_config = event['body']
    try:
        cluster_name = cluster_config['clusters'][0]['name']
    except KeyError as e:
        print(f'Invalid cluster config: {e}')

        raise e
    # Put into dynamodb cluster info
    ## cluster name should be unique cluster_config['clusters'][0]['name']
    ## server address cluster_config['clusters'][0]['cluster']['server']
    # Put into secrets manager
    ## user client-key-data cluster_config['users'][0]['name'] + cluster_config['users'][0]['user']['client-key-data']
    ## user client-certificate-data cluster_config['users'][0]['name'] + cluster_config['users'][0]['user']['client-certificate-data']
    ## user http name + password
    return {
        "statusCode": 200,
        "body": json.dumps(
            {"message": f'Cluster and config added {cluster_name}'}
        ),
    }

def validate_config_input(config):
    try:
        json.loads(config)
    except ValueError as err:
        print(f'K8s config is not valid json error: {err}')

#def validate_unique_cluster_name(cluster_name):
