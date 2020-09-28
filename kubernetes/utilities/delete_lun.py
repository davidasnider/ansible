#!/usr/bin/env python

import sys
from helper import (
    check_iscsi_target_to_extent_exists,
    check_iscsi_target_exists,
    check_iscsi_extent_exists,
    delete_target_to_extent,
    delete_target,
    delete_extent,
)

target_name = sys.argv[1]

if check_iscsi_target_to_extent_exists(target_name):
    if target_name != "rpimaster":
        delete_target_to_extent(target_name)
if check_iscsi_target_exists(target_name):
    if target_name != "rpimaster":
        delete_target(target_name)
if check_iscsi_extent_exists(target_name):
    if target_name != "rpimaster":
        delete_extent(target_name)
