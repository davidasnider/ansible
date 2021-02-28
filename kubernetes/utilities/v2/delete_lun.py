# Creates a lun given a command line argument

import models
import sys

# Get command line arguments
target_name = sys.argv[1]
pool = sys.argv[2]
snapshot = sys.argv[3]
dataset = sys.argv[4]

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
