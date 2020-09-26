![CI](https://github.com/davidasnider/ansible/workflows/CI/badge.svg)

# Ansible scripts for The Snider Pad

## Installing `hvac` inside brew

Brew installed Ansible does not have the hvac module enabled and requires
installation every time you update ansible. You must run the following command
to install `hvac`:

```bash
"$(brew --cellar ansible)/$(brew info ansible --json=v1 | jq -r '.[].linked_keg')/libexec/bin/pip" install hvac
```

## Secrets

Secrets are stored in https://vault.thesniderpad.com. We use the hashi_vault module to access those secrets.
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

```bash
ansible-playbook kubernetes/full_rebuild.yaml --extra-vars "cluster=k8s2"
```

## Testing new versions of kubernetes

1. It's likely a good idea to update the template node first
   1. Open Virtual Box, start `server.template`
   2. Login and run `apt-get update && apt-get upgrade`
2. Delete the old test environment
   1. `./delete_test_env.sh`
3. Create the new test environment
   1. `./create_test_env.sh`
4. Bootstrap ansible
   1. `ansible-playbook bootstrap/test-bootstrap.yaml -i test-inventory.yaml --extra-vars "cluster=k8stest"`
5. Install the latest playbooks
   1. `ansible-playbook site.yaml -i test-inventory.yaml`
