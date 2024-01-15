import pytest
import models


# The parent dataset to be tested against.
@pytest.fixture(scope="session")
def parent() -> str:
    return "SAMSUNG_1TB_NVME"


@pytest.fixture(scope="session")
def my_api():
    return models.freenas_api()


# Create the filesystem objects to be used in tests
@pytest.fixture(scope="session")
def base_zfs_dataset(parent, my_api):
    name = "deleteme"

    mylun = models.iscsi_lun(name=name, parent=parent, api_connection=my_api)
    mylun.create_dataset()
    mylun.create_extent(size=1024)
    mylun.create_dataset_snapshot("deleteme")
    mylun.extent_exists()
    yield
    mylun.delete_extent()
    mylun.delete_dataset_snapshot("deleteme")
    mylun.delete_dataset()


# Create a LUN to be used in tests.
@pytest.fixture(scope="session")
def test_lun(parent, my_api, base_zfs_dataset) -> str:
    # Setup
    mylun = models.iscsi_lun(
        name="deleteme-clone",
        parent=parent,
        api_connection=my_api,
        clone_from_snapshot="deleteme",
        clone_from_dataset="deleteme",
        extent_file="deleteme",
    )
    mylun.create_target()
    mylun.clone_dataset()
    mylun.create_extent()
    mylun.create_target_extent()

    yield mylun

    # Cleanup
    mylun.delete_target_extent()
    mylun.delete_extent()
    mylun.delete_dataset()
    mylun.delete_target()
