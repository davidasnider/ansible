seal "awskms" {
  region     = "us-west-2"
  access_key = "{{ vault_aws_access_key }}"
  secret_key = "{{ vault_aws_secret_key }}"
  kms_key_id = "{{ vault_aws_kms_key_id }}"
}

listener "tcp" {
  address     = "0.0.0.0:8200"
  tls_cert_file = "/certs/live/vault.thesniderpad.com/fullchain.pem"
  tls_key_file = "/certs/live/vault.thesniderpad.com/privkey.pem"
}

ui = true

storage "s3" {
  region     = "us-west-2"
  access_key = "{{ vault_aws_access_key }}"
  secret_key = "{{ vault_aws_secret_key }}"
  bucket     = "snidervault"
}