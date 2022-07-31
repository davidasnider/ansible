#!/bin/bash

set -euxo pipefail

# Fully update
apt update
apt -y upgrade
apt -y full-upgrade
apt install -y initramfs-tools open-iscsi
touch /etc/iscsi/iscsi.initramfs
update-initramfs -v -c -k $(uname -r)


# Mount the Root Partion in the Generated Image
TFTPROOT="$(mktemp -d)"
mount gw.thesniderpad.com:/tftproot/rpi4-boot $TFTPROOT

# Copy boot to tftp server
rsync -a --delete --progress /boot/ $TFTPROOT

# Mount the iscsi drive, format
iscsiadm \
  --mode discovery \
  --type sendtargets \
  --portal 10.9.0.6
iscsiadm \
  --mode node \
  --targetname iqn.2019-01.org.snider:rpi4master \
  --portal 10.9.0.6 \
  --login

# Wait for device to register in kernel
sleep 5

# Find the device name
ISCSI_DEVICE=$(readlink -f /dev/disk/by-path/*rpi4master-lun-0)
parted -s ${ISCSI_DEVICE} mklabel gpt
parted -s --align optimal ${ISCSI_DEVICE} mkpart primary ext4 0% 100%

# Wait for device to register in kernel
sleep 5

# Create the ext4 Filesystem
ISCSI_ROOT_PARTITION="${ISCSI_DEVICE}1"
mkfs.ext4 -F ${ISCSI_ROOT_PARTITION}
ISCSI_ROOT_DIR="$(mktemp -d)"
mount "${ISCSI_ROOT_PARTITION}" ${ISCSI_ROOT_DIR}

# Begin the Copy
rsync -a -x --info=progress2 / ${ISCSI_ROOT_DIR}

# Update / to point to the iSCSI drive.
ISCSI_ROOT_PARTUUID=$(sudo blkid ${ISCSI_ROOT_PARTITION} -o export |grep ^UUID | awk -F\= '{print $2}')
cat > /tmp/cmdline.txt <<EOF
dwc_otg.lpm_enable=0 modprobe.blacklist=bcm2835_v4l2 cgroup_enable=cpuset cgroup_memory=1 cgroup_enable=memory console=serial0,115200 console=tty1 ip=::::rpi4master:eth0:dhcp root=UUID=bb8dfde3-33a2-4359-9e20-d9cfbf111bdf rootfstype=ext4 elevator=deadline fsck.repair=yes rootwait qmap=fr ISCSI_INITIATOR=iqn.2019-01.org.rpi4master:RANDOM ISCSI_TARGET_NAME=iqn.2019-01.org.snider:rpi4master ISCSI_TARGET_IP=10.9.0.6 ISCSI_TARGET_PORT=3260 rw
EOF
cat /tmp/cmdline.txt | sed "s/UUID=[^ F]*/UUID=$ISCSI_ROOT_PARTUUID/" > $TFTPROOT/cmdline.txt

# Fix the fstab
cat /etc/fstab | grep -v PARTUUID > ${ISCSI_ROOT_DIR}/etc/fstab

# Update /boot/config.txt to use our new initramfs.
sed -i -r -e \
  "s@\[pi4\]@[pi4]\ninitramfs initrd.img-$(uname -r) followkernel@" \
  $TFTPROOT/config.txt

# The connection to the iSCSI device is no longer needed, so clean it up.
umount ${ISCSI_ROOT_DIR}
iscsiadm --m node -T iqn.2019-01.org.snider:rpi4master --portal 10.9.0.6:3260 -u
iscsiadm -m node -o delete -T iqn.2019-01.org.snider:rpi4master --portal 10.9.0.6:3260
umount $TFTPROOT
