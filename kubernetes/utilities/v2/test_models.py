import pytest
from v2 import models
import os


def test_target_crud(test_lun):
    # target created using fixture

    assert test_lun.target_exists()
    assert int(test_lun.get_target_details())


def test_freenas_api(my_api):
    response = my_api.get(uri="/api/v2.0/core/ping")
    assert response.ok
    assert response.text == '"pong"'


def test_zfs_crud(test_lun):
    # Dataset to clone comes from a fixture
    assert test_lun.dataset_exists()


def test_lun_extent_exists(test_lun):
    # Extent is created from fixture test_lun
    assert test_lun.extent_exists()
    assert int(test_lun.extent_id)


def test_link_target_to_extent(test_lun):
    # Extent target is created from fixture test_lun
    assert test_lun.target_extent_exists()
    assert int(test_lun.extent_target_id)
