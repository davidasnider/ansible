# This must be run once for any new pi 4's

# Find the latest eeprom
LATEST_EEPROM=$(ls -rt /lib/firmware/raspberrypi/bootloader/stable/pieeprom-*.bin | tail -n 1)
rpi-eeprom-config $LATEST_EEPROM > /tmp/bootconf.txt

# Enable pxe booting, and copy over additions.
grep -q '^BOOT_ORDER' /tmp/bootconf.txt && \
sed -i 's/BOOT_ORDER.*?$/BOOT_ORDER=0x21/g' /tmp/bootconf.txt || \
echo 'BOOT_ORDER=0x21' >> /tmp/bootconf.txt

# Save the new configuration to the firmware, and install it (requires a reboot).
rpi-eeprom-config --out /tmp/pieeprom-netboot.bin --config /tmp/bootconf.txt $LATEST_EEPROM
rpi-eeprom-update -d -f /tmp/pieeprom-netboot.bin

# Output the correct info for ansible
echo "MAC Address:"
ifconfig eth0|grep ether| awk '{print $2}'

echo "Serial Number:"
cat /proc/cpuinfo |grep ^Serial|awk '{print $3}'|cut -c 9-99

# wait to reboot
echo "Press enter to reboot, allow the device to reboot"
read anychar
shutdown -r now
