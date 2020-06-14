#!/bin/bash

for i in 1 2 3 4 5
do
    VBoxManage controlvm testserver${i} poweroff
    sleep 1
    VBoxManage unregistervm --delete testserver${i}

done
