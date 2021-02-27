import pytest
from v2 import models
import os


def test_instantiate_iscsi_lun(test_lun, parent, my_api):
    mylun = models.iscsi_lun(name=test_lun, parent=parent, api_connection=my_api)
    assert mylun.name == test_lun


def test_target_crud(test_lun, parent, my_api):
    mylun = models.iscsi_lun(name=test_lun, parent=parent, api_connection=my_api)
    assert mylun.create_target(test_lun)
    assert mylun.target_exits()
    assert int(mylun.get_target_details())
    assert mylun.delete_target()


def test_freenas_api(my_api):
    response = my_api.get(uri="/api/v2.0/core/ping")
    assert response.ok
    assert response.text == '"pong"'


def test_zfs_crud(test_lun, parent, base_zfs_dataset, my_api):
    # Dataset to clone comes from a fixture

    mylun = models.iscsi_lun(
        name=test_lun,
        parent=parent,
        clone_from_snapshot="deleteme",
        api_connection=my_api,
    )
    assert mylun.clone_dataset()
    assert mylun.delete_dataset()


def test_link_zfs_to_target():
    pass
