#!/bin/bash

if [[ $# -eq 0 ]] ; then
    echo 'You must specify the sub directory to create as the first argument'
    exit 0
fi

if [[ $# -eq 1 ]] ; then
    echo 'You must specify the host name as the second argument'
    exit 0
fi

cd /tftproot

if [[ -d $1 ]]
then
	echo "Directory exists, removing"
	rm -r $1
fi

mkdir $1

cp -r template/* $1

# Fix up the config
sed -i "s/rpimaster/$2/g" $1/cmdline.txt

UUID=$(uuidgen -r | awk -F - '{print $5}')

sed -i "s/RANDOM/$UUID/g" $1/cmdline.txt

