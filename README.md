# hyper-kube-config

hyper-kube-config - Provides a secure [Serverless](https://serverless.com/) API to store and retrieve [Kubernetes cluster config credentials](https://kubernetes.io/docs/tasks/access-application-cluster/configure-access-multiple-clusters/). hyper-kube-config leverages [AWS Secrets Manager](https://docs.aws.amazon.com/secretsmanager/index.html) for storing credential information.

![hyper-kube-config](https://user-images.githubusercontent.com/538171/46702337-8edc2780-cbd7-11e8-8ba5-dbbe9916708a.png)

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
  cluster_name=k8s-cluster.cloud
```

## Get user creds

```bash
http get \
  https://xxxxx.execute-api.us-west-2.amazonaws.com/dev/clusters/get-k8-config?foo-cluster.cloud \
  X-Api-Key:xxxx 
```

## Get user creds multiple clusters

```bash
http get \
  https://xxxxx.execute-api.us-west-2.amazonaws.com/dev/clusters/get-k8-config?foo-cluster.cloud&bar-cluster.cloud&baz-cluster.com \
  X-Api-Key:xxxx 
```

## List clusters

```bash
http get https://xxxxx.execute-api.us-west-2.amazonaws.com/dev/clusters/list X-Api-Key:xxxx 
```

## Requirements

* [Serverless](https://serverless.com/) - Serverless Framework
* [Docker](https://docker.com) - For serverless deploy
* [HTTPie](https://httpie.org/) - recommended for API client
* [serverless-python-requirements](https://www.npmjs.com/package/serverless-python-requirements) plugin. Uses Docker and Pip to package a newer vesion of Boto3 for AWS Lambda function use. AWS Lambda boto3 version by default doesn't have AWS Secrets Manager support for tags.

### Deploying 

```bash
sls deploy \
  --stage dev \
  --product k8s \
  --owner myteam@foo.cloud \
  --team myteam \
  --environment dev
```

Serverless will launch an [AWS API Gateway](https://docs.aws.amazon.com/apigateway/index.html) to handle API requests forwardered to [AWS Lambda functions](https://docs.aws.amazon.com/lambda/index.html#lang/en_us). A Dynamodb table is configured to store non-senstative cluster config details, while sensative information in uploaded configs (passwords and certs) is stored in [AWS Secrets Manager](https://docs.aws.amazon.com/secretsmanager/index.html).
