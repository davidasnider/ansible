There are two scripts in this directory.

- `create_nas_boot_img.sh` - This file is used to build a working image on the
  freenas server. It only needs to be run once from a freshly imaged sd card.
  TODO - make it an ansible script with reboots and such.
- `one_time_setup.sh` - This file must be run on every single Raspberry Pi 4.
  It sets up the network boot options. Allow it to fully reboot the machine
  after it runs.
  ```bash
  cat > /tmp/test.sh
  # Paste, followed by CTRL+D
  sudo bash /tmp/test.sh
  ```
- Test the network boot by removing the card and creating the boot directory
  on gw.thesniderpad.com
  ```
  cd /tftproot
  cp -r rpi4-boot <serial number>
  ```
