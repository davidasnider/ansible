"""
This script creates a LUN (Logical Unit Number) given command line arguments.
"""

import argparse
import logging
from v2 import models


def main(args):
    """
    Main function that creates a LUN using provided arguments.

    Parameters:
    args (argparse.Namespace): Command line arguments parsed by argparse.
    """

    # Instantiate the connection to freenas
    my_api = models.freenas_api()

    # Instantiate the iscsi_lun class
    mylun = models.iscsi_lun(
        name=args.target_name,
        parent=args.pool,
        api_connection=my_api,
        clone_from_snapshot=args.snapshot,
        clone_from_dataset=args.dataset,
        extent_file=args.extent_file,
        blocksize=args.blocksize,
    )

    mylun.clone_dataset()
    mylun.create_target()
    mylun.create_extent()
    mylun.create_target_extent()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Create a LUN.")
    parser.add_argument("target_name", help="Hostname in ansible")
    parser.add_argument("pool", help="Pool in ansible")
    parser.add_argument("snapshot", help="ZFS snapshot in ansible")
    parser.add_argument("dataset", help="Dataset snapshot in ansible")
    parser.add_argument("extent_file", help="Extent file")
    parser.add_argument("blocksize", help="Block size")

    args = parser.parse_args()

    logging.basicConfig(level=logging.INFO)

    main(args)
