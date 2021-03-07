# Creates a lun given a command line argument

import models
import sys

# Get command line arguments
target_name = sys.argv[1]  # Hostname in ansible
pool = sys.argv[2]  # pool in ansible
snapshot = sys.argv[3]  # zfs_snapshot in ansible
dataset = sys.argv[4]  # dataset_snapshot in ansible

# Instantiate the connection to freenas
my_api = models.freenas_api()

# Instantiate the iscsi_lun class
mylun = models.iscsi_lun(
    name=target_name,
    parent=pool,
    api_connection=my_api,
    clone_from_snapshot=snapshot,
    clone_from_dataset=dataset,
)


mylun.delete_target_extent()
mylun.delete_extent()
mylun.delete_target()
mylun.delete_dataset()
