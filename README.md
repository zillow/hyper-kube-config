# kube-auth-store

kube-auth-store - Provides a secure serverless API to store and retrieve k8s cluster credentials objects. kube-auth-store leverages AWS Secrets Manager for storing credential information. No trust API configuration requiring API key for access

## Post cluster and creds
```bash
kubectl config view --flatten -o json \
  | \
  http post \
  http://xxxxxxxx.execute-api.us-west-2.amazon.aws.com/dev/clusters/add \
  X-Api-Key:xxxx
```

## Remove cluster and creds
```bash
http post \
  https://xxxxxxxx.execute-api.us-west-2.amazonaws.com/dev/clusters/remove \
  X-Api-Key:xxxx \
  cluster_name=k8s-clustehr.cloud
```

## Get user creds
## Todo 
```bash
http get \
  https://xxxxx.execute-api.us-west-2.amazonaws.com/dev/clusters/get-k8-config?foo-cluster.cloud \
  X-Api-Key:xxxx 
```

## Todo

* Generate one config 
  - Return a Kube config file in yaml format with any number of clusters in it. Allowing end user to then switch context from one config
* Update creds based upon cluster and user input
* Delete indiviual creds based upon cluster and user input
* Add creds to existing cluster additional user configs for service or deploy users for example)
* Limit IAM access to bare requirements for kube-auth-store

## Requirements

* [Serverless](https://serverless.com/) - Serverless Framework
* [Docker](https://docker.com) - For serverless deploy
* [HTTPie](https://httpie.org/) - recommended for API client

### Deploying 

```bash
sls deploy --stage dev --domain mydomain.net
```