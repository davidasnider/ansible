import argparse
from delete_lun import get_args, main
import pytest
from unittest.mock import Mock
import models


def test_get_args(mocker):
    mocker.patch(
        "argparse.ArgumentParser.parse_args",
        return_value=argparse.Namespace(
            target_name="test_target",
            pool="test_pool",
            snapshot="test_snapshot",
            dataset="test_dataset",
        ),
    )

    args = get_args()

    assert args.target_name == "test_target"
    assert args.pool == "test_pool"
    assert args.snapshot == "test_snapshot"
    assert args.dataset == "test_dataset"


def test_main_exception_handling(mocker):
    # Mock the necessary objects and methods
    mocker.patch("models.freenas_api")
    mocker.patch("models.iscsi_lun")
    mocker.patch("sys.exit", side_effect=Exception("sys.exit was called"))

    # Create a mock for the iscsi_lun instance
    mock_iscsi_lun = models.iscsi_lun.return_value

    # Set the delete methods to raise an exception
    mock_iscsi_lun.delete_target_extent.side_effect = Exception("Test exception")

    args = Mock(
        target_name="test_target",
        pool="test_pool",
        snapshot="test_snapshot",
        dataset="test_dataset",
    )

    with pytest.raises(Exception, match="sys.exit was called"):
        main(args)
