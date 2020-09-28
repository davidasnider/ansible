#!/usr/bin/env python

import sys
from helper import (
    check_dataset_exists,
    create_dataset,
    check_iscsi_target_exists,
    create_iscsi_target,
    check_iscsi_extent_exists,
    create_iscsi_extent,
    check_iscsi_target_to_extent_exists,
    create_iscsi_target_to_extent,
)

target_name = sys.argv[1]
pool = sys.argv[2]
filename = sys.argv[3]
dataset = target_name + "_iscsi_luns"

# In our example, the datasets will all be under the parent, this is reflected in the API like 'parent/dataset'
dataset_exists = check_dataset_exists(pool, dataset)
if not dataset_exists:
    create_dataset(pool, dataset)

# Check to see if the iscsi target exists, if it does not, create it
target_exists = check_iscsi_target_exists(target_name)
if not target_exists:
    create_iscsi_target(target_name)

# Check to see if the iscsi extents exist, if it does not, create it
extent_exists = check_iscsi_extent_exists(target_name)
if not extent_exists:
    create_iscsi_extent(target_name, pool, dataset, filename)

# Check to see if the associated targets exist, if it does not, create it
target_to_extent_exists = check_iscsi_target_to_extent_exists(target_name)
if not target_to_extent_exists:
    create_iscsi_target_to_extent(target_name)
