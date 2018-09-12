# kube-auth-store

kube-auth-store - Provides a secure serverless API to store and retrieve k8s cluster credentials objects. kube-auth-store leverages AWS Secrets Manager for storing credential information. No trust API configuration requiring API key for access

## Post cluster and creds
```bash
curl \
  --header "X-Api-Key xxx" \
  -X POST \
  -d "$(kubectl get config --flatten -o json)"  \
  http://xxxxxxxx.execute-api.us-west-2.amazon.aws.com/dev/clusters/add
```

## Remove cluster and creds
```bash
curl \
  --header "Content-Type: application/json" \
  --header "X-Api-Key: xxx" \
  --request POST \
  --data '{ "cluster_name": "k8s-cluster.cloud"}' \
   https://xxxxxxxx.execute-api.us-west-2.amazonaws.com/dev/clusters/remove
```

## Todo

* Get creds 
  - Return a Kube config file in yaml format with any number of clusters in it. Allowing end user to then switch context from one config
* Update creds based upon cluster and user input
* Delete indiviual creds based upon cluster and user input
* Add creds to existing cluster (additional user configs for service or deploy users for example)
* Limit IAM access to bare requirements for kube-auth-store

## Requirements

* [Serverless](https://serverless.com/)

### Deploying 

```bash
sls deploy --stage dev --domain mydomain.net
```