# This is not really for Windows, it's for WSL

# Initialize repo dev and dependencies

In the parent directory of this one, `make setup-dev`

## Run playbook

### Occasionally update vault token

```bash
export VAULT_ADDR=https://vault.thesniderpad.com
vault login -method=userpass username=ansible
export VAULT_TOKEN=$(cat ~/.vault-token)
```

`ansible-playbook -K windows.yaml`
