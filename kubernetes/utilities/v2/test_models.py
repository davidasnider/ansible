import pytest
from v2 import models, create_lun, delete_lun
from unittest.mock import Mock, patch
import logging


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
def test_create_lun_main():
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


@pytest.mark.unittest
def test_delete_lun_main():
    # Mock the command line arguments
    args = Mock()
    args.target_name = "test_target"
    args.pool = "test_pool"
    args.snapshot = "test_snapshot"
    args.dataset = "test_dataset"

    # Mock the freenas_api and iscsi_lun classes
    with patch.object(models, "freenas_api") as mock_freenas_api, patch.object(
        models, "iscsi_lun"
    ) as mock_iscsi_lun:
        # Mock the iscsi_lun instance
        mock_lun = Mock()
        mock_iscsi_lun.return_value = mock_lun

        # Call the main function
        delete_lun.main(args)

        # Check that the freenas_api and iscsi_lun classes were instantiated correctly
        mock_freenas_api.assert_called_once_with()
        mock_iscsi_lun.assert_called_once_with(
            name=args.target_name,
            parent=args.pool,
            api_connection=mock_freenas_api.return_value,
            clone_from_snapshot=args.snapshot,
            clone_from_dataset=args.dataset,
        )

        # Check that the methods of the iscsi_lun instance were called correctly
        mock_lun.delete_target_extent.assert_called_once_with()
        mock_lun.delete_extent.assert_called_once_with()
        mock_lun.delete_target.assert_called_once_with()
        mock_lun.delete_dataset.assert_called_once_with()


@pytest.mark.unittest
def test_get_logger():
    # Mock the logging module
    with patch.object(logging, "getLogger") as mock_getLogger, patch.object(
        logging, "StreamHandler"
    ) as mock_StreamHandler, patch.object(logging, "Formatter") as mock_Formatter:
        # Mock the logger and handler instances
        mock_logger = Mock()
        mock_getLogger.return_value = mock_logger
        mock_handler = Mock()
        mock_StreamHandler.return_value = mock_handler

        # Override the hasHandlers method to return True
        mock_logger.hasHandlers.return_value = False

        # Call the get_logger function
        logger = models.get_logger()

        # Check that the logging module was used correctly
        mock_getLogger.assert_called_once_with("v2.models")
        mock_StreamHandler.assert_called_once_with()
        mock_handler.setLevel.assert_called_once_with(logging.WARNING)
        mock_Formatter.assert_called_once_with(
            "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        )
        mock_handler.setFormatter.assert_called_once_with(mock_Formatter.return_value)
        mock_logger.addHandler.assert_called_once_with(mock_handler)

        # Check that the correct logger was returned
        assert logger == mock_logger

        # Check that the logger has at least one handler
        assert logger.hasHandlers() is False
