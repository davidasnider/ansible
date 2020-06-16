# Ansible scripts for The Snider Pad

## Secrets

A few necessary "bootstrap" style secrets are stored in an ansible vault file. These are necessary
for setting up the vault server itself, as well as the access token to access vault. All other
secrets are stored in https://vault.thesniderpad.com

## Common use cases

### Apply all playbooks

```
ansible-playbook site.yaml
```

### Apply all playbooks to a specific group or host

In this case, we limit the run to nodes in the k8s2 group

```
ansible-playbook site.yaml -l k8s2
```

### Rebuild the kubernetes clusters

```
ansible-playbook kubernetes/full_rebuild.yaml --extra-vars "cluster=k8s2"
```


# Testing new versions

1. Delete the old test environment
   1. `./delete_test_env.sh`
2. Create the new test environment
   1. `./create_test_env.sh`
3. Bootstrap ansible
   1. `ansible-playbook bootstrap/test-bootstrap.yaml -i test-inventory.yaml --extra-vars "cluster=k8stest"`
4. Install the latest playbooks
   1. `ansible-playbook site.yaml -i test-inventory.yaml`
