import argparse
from create_lun import get_args


def test_get_args(mocker):
    mocker.patch(
        "argparse.ArgumentParser.parse_args",
        return_value=argparse.Namespace(
            target_name="test_target",
            pool="test_pool",
            snapshot="test_snapshot",
            dataset="test_dataset",
            extent_file="test_extent_file",
            blocksize="test_blocksize",
        ),
    )

    args = get_args()

    assert args.target_name == "test_target"
    assert args.pool == "test_pool"
    assert args.snapshot == "test_snapshot"
    assert args.dataset == "test_dataset"
    assert args.extent_file == "test_extent_file"
    assert args.blocksize == "test_blocksize"
