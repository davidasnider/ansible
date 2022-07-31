# Creating a new bootable Intel Image for ISCSI Boot

## Download the latest Debian Installation ISO

Download and install the netinst image from [here](https://www.debian.org/devel/debian-installer/)

NOTE: Currently Debian Bullseye does not find the iSCSI disks on Truenas. Use
Buster instead and upgrade post image creation.

## Boot virtual box

1. Ensure the virtual box vm is set to boot from the downloaded CD image.

1. Boot the virtual box vm, pressing escape to bypass the PXE boot.

1. Follow all standard steps until you reach the point that you are prompted to
   select a disk to install to.

1. Select install without a disk, you will be prompted to "Configure iSCSI volumes"

   1. Use 10.9.0.6:3260 as the target
   1. Remove the swap partition
   1. Continue the install as normal

1. Install only SSH Server and standard system utilities

1. Upon reboot, you will need to configure the new image:

   1. Follow the instructions [here](https://linuxize.com/post/how-to-upgrade-debian-10-to-debian-11/)
      to upgrade the image to bullseye
   1. Say OK to all of the prompts

1. Install non-free firmware for realtek, edit `/etc/apt/sources.list`:

   1. replace the lines for `main` with:

   ```text
   deb http://deb.debian.org/debian/ bullseye main contrib non-free
   deb-src http://deb.debian.org/debian/ bullseye main contrib non-free
   ```

   1. run `apt update`, then `apt install firmware-realtek`, then
      `update-initramfs -c -k all`

1. Make grub boot faster with no timeout

   1. `vi /etc/default/grub`
   1. Change the GRUB_TIMETOUT line to `GRUB_TIMEOUT=1`
   1. Save and exit vi
   1. `sudo update-grub`

1. Fix the network hang on shutdown

   1. `vi /etc/network/interfaces`
   1. Comment out all lines dealing with the primary network interface

1. Make iscsi dynamic

   1. `vi /etc/iscsi/iscsi.initramfs`
   1. replace all lines with `ISCSI_AUTO=true`
   1. `update-initramfs -c -k all`

1. Reboot and make sure all is still functional

## Take a snapshot of the image and rebuild kubernetes

1. Login to the TrueNas server.
1. Go to Storage -> Pools -> iamaster_iscsi_luns
1. Create a snapshot, with the format YYYMMDD

## Update Ansible playbooks

1. `code ~/code/ansible`
1.
