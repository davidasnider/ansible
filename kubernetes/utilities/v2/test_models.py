import pytest
from v2 import models, create_lun
import os
from unittest.mock import Mock, patch


@pytest.mark.integration
def test_target_crud(test_lun):
    # target created using fixture

    assert test_lun.target_exists()
    assert int(test_lun.get_target_details())


@pytest.mark.integration
def test_freenas_api(my_api):
    response = my_api.get(uri="/api/v2.0/core/ping")
    assert response.ok
    assert response.text == '"pong"'


@pytest.mark.integration
def test_zfs_crud(test_lun):
    # Dataset to clone comes from a fixture
    assert test_lun.dataset_exists()


@pytest.mark.integration
def test_lun_extent_exists(test_lun):
    # Extent is created from fixture test_lun
    assert test_lun.extent_exists()
    assert int(test_lun.extent_id)


@pytest.mark.integration
def test_link_target_to_extent(test_lun):
    # Extent target is created from fixture test_lun
    assert test_lun.target_extent_exists()
    assert int(test_lun.extent_target_id)


@pytest.mark.unittest
def test_main():
    args = Mock(
        target_name="target",
        pool="pool",
        snapshot="snapshot",
        dataset="dataset",
        extent_file="extent_file",
        blocksize="blocksize",
    )

    with patch.object(models, "freenas_api") as mock_freenas_api, patch.object(
        models, "iscsi_lun"
    ) as mock_iscsi_lun:
        instance = mock_iscsi_lun.return_value
        instance.clone_dataset = Mock()
        instance.create_target = Mock()
        instance.create_extent = Mock()
        instance.create_target_extent = Mock()

        create_lun.main(args)

        mock_freenas_api.assert_called_once()
        mock_iscsi_lun.assert_called_once_with(
            name=args.target_name,
            parent=args.pool,
            api_connection=mock_freenas_api.return_value,
            clone_from_snapshot=args.snapshot,
            clone_from_dataset=args.dataset,
            extent_file=args.extent_file,
            blocksize=args.blocksize,
        )
        instance.clone_dataset.assert_called_once()
        instance.create_target.assert_called_once()
        instance.create_extent.assert_called_once()
        instance.create_target_extent.assert_called_once()
