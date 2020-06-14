#!/bin/bash

for i in 1 2 3 4 5
do
    VBoxManage clonevm server.template --register --name=testserver${i} --options=Link --snapshot="clone"
    VBoxManage modifyvm testserver${i} --macaddress1 08002712f60${i}
    VBoxManage startvm testserver${i}
done
