#!/bin/sh

errorExit() {
    echo "*** $*" 1>&2
    exit 1
}

curl --silent --max-time 2 --insecure https://localhost:6443/healthz | grep ok || errorExit "Error GET https://localhost:6443/healthz"
if ip addr | grep -q {{ vip }}; then
    curl --silent --max-time 2 --insecure https://{{ vip }}:6443/healthz | grep ok || errorExit "Error GET https://{{ ip }}:6443/healthz"
fi
