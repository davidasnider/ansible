# This is a pain in the ass.  Just install packages with chocolatey

Run the below code from an adminsitrative powershell window

## Install Chocolatey

```
Set-ExecutionPolicy Bypass -Scope Process -Force; iex ((New-Object System.Net.WebClient).DownloadString('https://chocolatey.org/install.ps1'))
```

## Packages to install

```
vscode
steam
git
```

# Setup the Windows Host

Run the below code from an administrative powershell window

```
$url = "https://raw.githubusercontent.com/ansible/ansible/devel/examples/scripts/ConfigureRemotingForAnsible.ps1"
$file = "$env:temp\ConfigureRemotingForAnsible.ps1"

(New-Object -TypeName System.Net.WebClient).DownloadFile($url, $file)

powershell.exe -ExecutionPolicy ByPass -File $file
```

Validate the winrm service is setup

```
winrm enumerate winrm/config/Listener
```

ansible-playbook config.yaml -K
