# hyper-kube-config CHANGELOG

This file is used to list changes made in each version of hyper-kube-config.

## unreleased

## 0.5.0 (2020-04-20)
- [Nolan Emirot]
  - Add travis stages (test, lint)

## 0.5.0 (2020-04-17)
- [Christopher Zorn]
  - Make sure returned json in lambda handlers are consistent in cluster status handlers.
  - Make sure stdout in cli tool is valid json
  - Add support for multiple environments for a cluster. This allows for tagging workload environments along with cluster environments.

## 0.2.0 (2020-03-02)
- [Zane Williamson] - Moving moto to dev-packages, changing short flag for environment from '-g' to '-e' (breaking change)

## 0.1.8 (2020-03-02)
- [Christopher Zorn] - Adding tests, adding get-cluster-for-environment lookup, new storage module

## 0.1.7 (2019-10-18)
- [Swarup Donepudi]
  - Provide the option to user for `get` and `get-all` to merge with existing `~/.kube/config` or whatever the user passes using the option `-k`

## 0.1.6 (2019-10-17)
- [Nolan  Emirot]
  - Sort cluster list output in kubectl hyperkube

## 0.1.5 (2019-09-16)
- [Zane Williamson, Christopher Zorn]
  - Allow cluster-authority-data to be an optional input
  - updating dependencies 
  - Flake changes, also run flake in travis

## 0.1.4 (2019-06-03)
- [Swarup Donepudi]
  - Fix reading from default config

## 0.1.3 (2019-05-31)
- [Zane Williamson]
  - Fixing get and get all commands

## 0.1.2 (2019-05-24)
- [Zane Williamson]
  - Adding support for adding CA key for k8s cluster

## 0.1.1 (2019-05-23)
- [Zane Williamson]
  - Adding get-all command: retrieve and concatenate all cluster configs into one config

## 0.1.0 (2019-05-14)
- [Zane Williamson] 
  - Adding support to store and associate Pems to a cluster
  - Adding support to set and get arbitrary status and environment strings to a cluster

## 0.0.3 (2018-04-01)
- [Akshay Raj] - Fixed fixed YAMLLoadWarning 

## 0.0.2 (2018-12-18)
- [Zane Williamson] - Updating to handle 404 response with exit code 1 

## 0.0.1 (2018-12-18)
- [Zane Williamson] - Initial release to PyPi 
