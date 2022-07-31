# Bootstrap notes

## Raspberry Pi

### First, image the SD Card

1. Download the latest image from raspbian
1. Image it with the below command, change the disk and image name appropriately

```
diskutil unmountDisk /dev/disk2 && sudo dd bs=1m if=2019-09-26-raspbian-buster-lite.img of=/dev/rdisk2 conv=sync && sleep 10 && touch /Volumes/boot/ssh && diskutil unmountDisk /dev/disk2
```

# Bootstrap a new client Manually

1. From the PARENT directory, run the following command:
1. Raspbian based hosts
   `ansible-playbook bootstrap/rpi_init.yaml --extra-vars "cluster=grigio"`
