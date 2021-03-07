# Creates a lun given a command line argument

import models
import sys

# Get command line arguments
target_name = sys.argv[1]  # Hostname in ansible
pool = sys.argv[2]  # pool in ansible
snapshot = sys.argv[3]  # zfs_snapshot in ansible
dataset = sys.argv[4]  # datset_snapshot in ansible
extent_file = sys.argv[5]
blocksize = sys.argv[6]

# Instantiate the connection to freenas
my_api = models.freenas_api()

# Instantiate the iscsi_lun class
mylun = models.iscsi_lun(
    name=target_name,
    parent=pool,
    api_connection=my_api,
    clone_from_snapshot=snapshot,
    clone_from_dataset=dataset,
    extent_file=extent_file,
    blocksize=blocksize,
)

mylun.clone_dataset()
mylun.create_target()
mylun.create_extent()
mylun.create_target_extent()
