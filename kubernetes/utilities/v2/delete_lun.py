import argparse
import models
import sys
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


def main(args):
    # Instantiate the connection to freenas
    my_api = models.freenas_api()

    # Instantiate the iscsi_lun class
    mylun = models.iscsi_lun(
        name=args.target_name,
        parent=args.pool,
        api_connection=my_api,
        clone_from_snapshot=args.snapshot,
        clone_from_dataset=args.dataset,
    )

    try:
        mylun.delete_target_extent()
        mylun.delete_extent()
        mylun.delete_target()
        mylun.delete_dataset()
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)


def get_args():
    parser = argparse.ArgumentParser(description="Delete a LUN.")
    parser.add_argument("--target_name", help="The target name")
    parser.add_argument("--pool", help="The pool name")
    parser.add_argument("--snapshot", help="The snapshot name")
    parser.add_argument("--dataset", help="The dataset name")

    args = parser.parse_args()
    return args


if __name__ == "__main__":

    main(get_args())
