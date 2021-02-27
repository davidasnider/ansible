import pytest
from v2 import models


@pytest.fixture
def test_lun() -> str:
    return "deleteme-clone"


@pytest.fixture
def parent() -> str:
    return "SAMSUNG_1TB_NVME"


@pytest.fixture
def my_api():
    return models.freenas_api()


@pytest.fixture
def base_zfs_dataset(
    name="deleteme", parent="SAMSUNG_1TB_NVME", api_connection=models.freenas_api()
):
    mylun = models.iscsi_lun(name=name, parent=parent, api_connection=api_connection)
    mylun.create_dataset()
    mylun.create_dataset_snapshot("deleteme")
    yield mylun
    mylun.delete_dataset_snapshot("deleteme")
    mylun.delete_dataset()
