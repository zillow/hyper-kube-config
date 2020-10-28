# Migrating from API Key to IAM Auth Access

1. Upgrade to kubectl-hyperkube plugin to 0.6.0 or newer

   ```pip install hyper-kube-config --upgrade```

2. Ensure where you are running kubectl-hyperkube cli commands you are using AWS credentials that you will then whitelist (based upon role, user, or account) in [AWS API Gateway Resource Policy](https://docs.aws.amazon.com/apigateway/latest/developerguide/apigateway-resource-policies.html)

3. Turn on AWS API Gateway Resource Policy and enable `AWS_IAM` authentication on lambdas.

See example config with this type of access: [example](../serverless.yml.example_iam_policy_access)

example to give account, user and role access:
  ```
  ---snip---
  resourcePolicy:
    - Effect: Allow
      Principal:
      AWS:
        - arn:aws:iam::{{ExampleAWSAccountID}}:root
        - arn:aws:iam::{{ExampleAWSAccountID}}:user/{{ExampleAWSUserName}}
        - arn:aws:iam::{{ExampleAWSAccountID}}:role/{{ExampleAWSRoleName}}
      Action: execute-api:Invoke
      Resource:
        - execute-api:/${opt:stage}/POST/clusters/add
        - execute-api:/${opt:stage}/POST/clusters/add-ca-key
        - execute-api:/${opt:stage}/POST/clusters/add-pem
        - execute-api:/${opt:stage}/GET/clusters/cluster-status
        - execute-api:/${opt:stage}/GET/clusters/clusters-per-environment
        - execute-api:/${opt:stage}/GET/clusters/get-all-k8-configs
        - execute-api:/${opt:stage}/GET/clusters/get-cluster-metadata
        - execute-api:/${opt:stage}/GET/clusters/get-k8s-config
        - execute-api:/${opt:stage}/GET/clusters/get-pem
        - execute-api:/${opt:stage}/GET/clusters/list
        - execute-api:/${opt:stage}/POST/clusters/remove
        - execute-api:/${opt:stage}/GET/clusters/remove-ca-key
        - execute-api:/${opt:stage}/GET/clusters/remove-pem
        - execute-api:/${opt:stage}/POST/clusters/set-cluster-metadata
        - execute-api:/${opt:stage}/GET/clusters/set-cluster-environment
        - execute-api:/${opt:stage}/GET/clusters/set-cluster-status
  --snip--
```

Each function will also need to have 'authorizer' set to `aws_iam`. Step 3 needs to be done all at once.
