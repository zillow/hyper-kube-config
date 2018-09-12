# kube-auth-store

kube-auth-store - Provides a secure serverless API to store and retrieve k8s cluster credentials objects. kube-auth-store leverages AWS Secrets Manager for storing credential information. No trust API configuration requiring API key for access

## Post cluster and creds
```bash
curl --header "X-Api-Key xxx" -X POST -d "$(kubectl get config --flatten -o json)" http://xxxxxxxx.execute-api.us-west-2.amazon.aws.com/dev/clusters/add
```

## Todo

* Get creds 
  - Return a Kube config file in yaml format with any number of clusters in it. Allowing end user to then switch context from one config
* Delete creds
* Update creds
* Add creds to existing cluster (additional user configs for service or deploy users for example)
* Limit IAM access to bare requirements

## Requirements

* [Serverless](https://serverless.com/)

### Deploying 

```bash
sls deploy --stage dev --domain mydomain.net
```