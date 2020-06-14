#!/bin/bash

# What disks do we have on the NAS?
DISKS=$(zfs list | awk '{ print $1 }' | egrep -v "NAME|freenas-boot|SAMSUNG_1TB_NVME|\/")

# What is the last snapshot of the Raspberry Pi master image?
FULL_RPI_SNAPSHOT_PATH=$(zfs list -t snapshot -r SAMSUNG_1TB_NVME/rpimaster_iscsi_luns| grep rpimaster | awk '{print $1}'| tail -n 1)
RPI_SNAPSHOT_VERSION=$(echo $FULL_RPI_SNAPSHOT_PATH| cut -d @ -f 2)

# Get the destination last snapshot for Raspberry pi
for i in $DISKS
do
        if [ ! -d /mnt/$i/rpimaster_iscsi_luns ]
        then
                zfs set compression=off $i
                zfs send $FULL_RPI_SNAPSHOT_PATH | zfs receive $i/rpimaster_iscsi_luns
                zfs set compression=off $i/rpimaster_iscsi_luns
                zfs set compression=lz4 $i
        fi

        DEST_RPI_SNAPSHOT_PATH=$(zfs list -t snapshot -r $i/rpimaster_iscsi_luns| grep rpimaster | awk '{print $1}'| tail -n 1)
        DEST_RPI_SNAPSHOT_VERSION=$(echo $DEST_RPI_SNAPSHOT_PATH| cut -d @ -f 2)

        if [ "$RPI_SNAPSHOT_VERSION" != "$DEST_RPI_SNAPSHOT_VERSION" ]
        then
                # Make sure no modifications have occured
                zfs rollback $i/rpimaster_iscsi_luns@$DEST_RPI_SNAPSHOT_VERSION

                # Send incremental changes
                zfs send -I SAMSUNG_1TB_NVME/rpimaster_iscsi_luns@$DEST_RPI_SNAPSHOT_VERSION SAMSUNG_1TB_NVME/rpimaster_iscsi_luns@$RPI_SNAPSHOT_VERSION | zfs receive $i/rpimaster_iscsi_luns
        fi

done

# What is the last snapshot of the Intel Atom master image?
FULL_IA_SNAPSHOT_PATH=$(zfs list -t snapshot -r SAMSUNG_1TB_NVME/iamaster_iscsi_luns| grep iamaster | awk '{print $1}'| tail -n 1)
IA_SNAPSHOT_VERSION=$(echo $FULL_IA_SNAPSHOT_PATH| cut -d @ -f 2)

# Get the destination last snapshot for Intel Atom
for i in $DISKS
do
        if [ ! -d /mnt/$i/iamaster_iscsi_luns ]
        then
                zfs set compression=off $i
                zfs send $FULL_IA_SNAPSHOT_PATH | zfs receive $i/iamaster_iscsi_luns
                zfs set compression=off $i/iamaster_iscsi_luns
                zfs set compression=lz4 $i
        fi

        DEST_IA_SNAPSHOT_PATH=$(zfs list -t snapshot -r $i/iamaster_iscsi_luns| grep iamaster | awk '{print $1}'| tail -n 1)
        DEST_IA_SNAPSHOT_VERSION=$(echo $DEST_IA_SNAPSHOT_PATH| cut -d @ -f 2)

        if [ "$IA_SNAPSHOT_VERSION" != "$DEST_IA_SNAPSHOT_VERSION" ]
        then
                # Make sure no modifications have occured
                zfs rollback $i/iamaster_iscsi_luns@$DEST_IA_SNAPSHOT_VERSION

                # Send incremental changes
                zfs send -I SAMSUNG_1TB_NVME/iamaster_iscsi_luns@$DEST_IA_SNAPSHOT_VERSION SAMSUNG_1TB_NVME/iamaster_iscsi_luns@$IA_SNAPSHOT_VERSION | zfs receive $i/iamaster_iscsi_luns
        fi

done
