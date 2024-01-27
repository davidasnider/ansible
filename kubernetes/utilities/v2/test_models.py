import pytest
import models
import create_lun
import delete_lun
from unittest.mock import Mock, patch
import logging
from models import get_logger, log_config, iscsi_lun, freenas_api


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


def test_get_logger():
    logger = get_logger()

    # Check if the logger has the correct name
    assert logger.name == "models"

    # Check if the logger has any handlers
    assert logger.hasHandlers() is True

    # Check if the logger has a StreamHandler
    assert any(
        isinstance(handler, logging.StreamHandler) for handler in logger.handlers
    )

    # Check if the StreamHandler has the correct log level
    assert any(
        handler.level == 20
        for handler in logger.handlers
        if isinstance(handler, logging.StreamHandler)
    )

    # Check if the StreamHandler has the correct formatter
    assert any(
        isinstance(handler.formatter, logging.Formatter)
        for handler in logger.handlers
        if isinstance(handler, logging.StreamHandler)
    )


def test_get_logger_no_handlers(mocker):
    # Get the logger
    logger = get_logger()

    # Mock the hasHandlers method to always return False
    mocker.patch.object(logger, "hasHandlers", return_value=False)

    # Call get_logger again
    logger = get_logger()

    # Check if the logger has a StreamHandler
    assert any(
        isinstance(handler, logging.StreamHandler) for handler in logger.handlers
    )

    # Check if the StreamHandler has the correct log level
    assert any(
        handler.level == logging.WARNING
        for handler in logger.handlers
        if isinstance(handler, logging.StreamHandler)
    )

    # Check if the StreamHandler has the correct formatter
    assert any(
        isinstance(handler.formatter, logging.Formatter)
        for handler in logger.handlers
        if isinstance(handler, logging.StreamHandler)
    )


def test_log_config():
    config_dict = log_config()

    # Check if the returned value is a dictionary
    assert isinstance(config_dict, dict)

    # Check if the dictionary is not empty
    assert bool(config_dict)

    # Optionally, check for specific keys in the dictionary
    # Replace 'key1' and 'key2' with actual keys you expect in the dictionary
    assert "version" in config_dict
    assert "disable_existing_loggers" in config_dict
    assert "handlers" in config_dict
    assert "formatters" in config_dict
    assert "loggers" in config_dict


def test_delete_target_does_not_exist(mocker):
    # Mock the necessary objects and methods
    mocker.patch.object(iscsi_lun, "target_exists", return_value=False)
    mocker.patch("models.log")

    # Instantiate the connection to freenas
    my_api = freenas_api()

    # Instantiate the iscsi_lun class
    instance = iscsi_lun(
        name="test_target", parent="test_parent", api_connection=my_api
    )

    # Call delete_target
    response = instance.delete_target()

    # Check if the log.info method was called with the correct arguments
    models.log.info.assert_called_once_with(f"Target {instance.name} does not exist")
    # Check if the response is None
    assert response is None


def test_delete_dataset_does_not_exist(mocker):
    # Mock the necessary objects and methods
    mocker.patch.object(iscsi_lun, "dataset_exists", return_value=False)
    mocker.patch("models.log")

    # Instantiate the connection to freenas
    my_api = freenas_api()

    # Instantiate the iscsi_lun class
    instance = iscsi_lun(
        name="test_target", parent="test_parent", api_connection=my_api
    )

    # Call delete_target
    response = instance.delete_dataset()

    # Check if the log.info method was called with the correct arguments
    models.log.info.assert_called_once_with(f"Dataset {instance.name} does not exist")
    # Check if the response is False
    assert response is False


def test_delete_extent_does_not_exist(mocker):
    # Mock the necessary objects and methods
    mocker.patch.object(iscsi_lun, "extent_exists", return_value=False)
    mocker.patch("models.log")

    # Instantiate the connection to freenas
    my_api = freenas_api()

    # Instantiate the iscsi_lun class
    instance = iscsi_lun(
        name="test_target", parent="test_parent", api_connection=my_api
    )

    # Call delete_target
    response = instance.delete_extent()

    # Check if the log.info method was called with the correct arguments
    models.log.info.assert_called_once_with(f"Extent {instance.name} does not exist")
    # Check if the response is None
    assert response is None
