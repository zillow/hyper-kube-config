import sys
import yaml
import json

def _parse_kube_config(filename):
    try:
        data = open(filename).read()

        # yaml.load seems to tolerate json too!
        config = yaml.load(data, Loader=yaml.FullLoader)

        return config
    except Exception as e:
        print(e)
        sys.exit -1

def merge(source_files, target_file):
  parsed = [_parse_kube_config(file) for file in source_files]

  # Now do an effective flatmap to get it all into a single structure
  target_config = {
      "apiVersion": "v1",
      "kind": "Config",
      "current-context": "",
      "clusters": [],
      "contexts": [],
      "users": [],
  }

  for config in parsed:
      for cluster in config['clusters']:
          target_config['clusters'].append(cluster)
      for context in config['contexts']:
          target_config['contexts'].append(context)
      for user in config['users']:
          target_config['users'].append(user)

  open(target_file, 'w').write(yaml.dump(target_config))
