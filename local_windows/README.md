# This is not really for Windows, it's for WSL

## Install ansible on WSL

apt upgrade && apt install ansible

## Run playbook

### Occasionally update vault token

```bash
export VAULT_ADDR=https://vault.thesniderpad.com
vault login -method=userpass username=ansible
export VAULT_TOKEN=$(cat ~/.vault-token)
```

`ansible-playbook -K windows.yaml`
