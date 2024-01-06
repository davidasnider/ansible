# Ansible scripts for The Snider Pad

![CI](https://github.com/davidasnider/ansible/workflows/CI/badge.svg)

## Setup runtime/dev workstation

All configuration needed for development setup is in the Makefile.

`make setup-dev`

## Activate Python Virtual Environment

Ansible is installed via Poetry. (this is done automatically in VS Code)

`source .venv/bin/activate`

## Secrets

Secrets are stored in [vault](https://vault.thesniderpad.com). We use the hashi_vault module to access those secrets.
You must have a valid token stored in the `VAULT_TOKEN` variable, run these commands before running any of
the below commands:

```bash
vault login -method=userpass username=ansible
export VAULT_TOKEN=$(cat ~/.vault-token)
```

## Common use cases

### Apply all playbooks

```bash
ansible-playbook site.yaml
```

### Apply all playbooks to a specific group or host

In this case, we limit the run to nodes in the k8s2 group

```bash
ansible-playbook site.yaml -l k8s2
```

### Rebuild the kubernetes clusters

NOTE: If you find that some of the nodes are not properly rebuilding, try resetting
the iSCSI service on the TrueNas server.

````bash

```bash
ansible-playbook kubernetes/full_rebuild.yaml --extra-vars "cluster=k8s1"
````

## Testing new versions of kubernetes

1. It's likely a good idea to update the template node first
   1. Open Virtual Box, start `server.template`
   1. Login and run `apt-get update && apt-get upgrade`
1. Delete the old test environment
   1. `./delete_test_env.sh`
1. Create the new test environment
   1. `./create_test_env.sh`
1. Bootstrap ansible
   1. `ansible-playbook bootstrap/test-bootstrap.yaml -i test-inventory.yaml --extra-vars "cluster=k8stest"`
1. Install the latest playbooks
   1. `ansible-playbook site.yaml -i test-inventory.yaml`

## Updating local pv-provisioner

```
   cd ~/code/sig-storage-local-static-provisioner
   git pull
   helm template ./helm/provisioner -f ./helm/provisioner/values.yaml --namespace pv-provisioner > ~/code/ansible/roles/prod_services/files/provisioner-generated.yaml
```
