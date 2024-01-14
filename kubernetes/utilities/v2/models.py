from pydantic import BaseModel, HttpUrl
from pydantic_settings import BaseSettings
import requests
from requests.auth import HTTPBasicAuth
import json
import yaml
import logging.config
import pathlib

LOGGING_CONFIG = pathlib.Path(__file__).parent / "logging.yaml"

with open(LOGGING_CONFIG) as f:
    config_dict = yaml.safe_load(f)
    logging.config.dictConfig(config_dict)


# get root logger
def log():
    return logging.getLogger(__name__)
    # the __name__ resolve to "main" since we are at the root of the project
    # This will get the root logger since no logger in the configuration has this name.


def log_config():
    return config_dict


log = log()


class freenas_api(BaseSettings):
    url: HttpUrl
    username: str
    password: str

    def auth(self):
        return HTTPBasicAuth(self.username, self.password)

    def get(self, uri):
        get_url = str(self.url) + uri
        response = requests.request("GET", get_url, auth=self.auth(), verify=False)
        log.info(f"Freenas Get {get_url}, good response: {response.ok}")
        return response

    def post(self, uri, headers={}, data={}):
        post_url = str(self.url) + uri
        response = requests.post(
            url=post_url,
            auth=self.auth(),
            headers=headers,
            data=json.dumps(data),
            verify=False,
        )
        log.info(f"Freenas Post {post_url}, good response: {response.ok}")
        return response

    def delete(self, uri, data={}) -> bool:
        headers = {
            "Content-Type": "application/json",
        }
        post_url = str(self.url) + uri
        response = requests.request(
            "DELETE",
            post_url,
            headers=headers,
            data=json.dumps(data),
            auth=self.auth(),
            verify=False,
        )
        log.info(f"Freenas Post {post_url}, good response: {response.ok}")
        return response.ok


class iscsi_lun(BaseModel):
    """
    The iqn LUN for iscsi devices
    """

    name: str
    parent: str
    api_connection: freenas_api
    clone_from_snapshot: str = None
    clone_from_dataset: str = None
    extent_id: int = None
    target_id: int = None
    extent_target_id: int = None
    extent_file: str = None
    blocksize: int = 512

    def target_exists(self):
        url = "/api/v2.0/iscsi/target?name=" + self.name
        response = self.api_connection.get(url)
        exists = False
        for response_item in response.json():
            if response_item["name"] == self.name:
                exists = True
                self.target_id = response_item["id"]
        log.info(f"Target {self.name} Exists: {exists}")
        return exists

    def get_target_details(self):
        url = "/api/v2.0/iscsi/target?name=" + self.name
        response = self.api_connection.get(url)
        id = None
        for response_item in response.json():
            if response_item["name"] == self.name:
                id = response_item["id"]
        log.info(f"Target {self.name} has id: {id}")
        return id

    def create_target(self) -> bool:
        url = "/api/v2.0/iscsi/target"
        payload = {
            "name": self.name,
            "alias": self.name,
            "mode": "ISCSI",
            "groups": [
                {"portal": 1, "initiator": 1, "auth": None, "authmethod": "NONE"}
            ],
        }
        response = self.api_connection.post(url, data=payload)
        if response.ok:
            self.target_id = response.json()["id"]
        log.info(f"Target {self.name} created: {response.ok}")
        return response.ok

    def delete_target(self):
        if self.target_exists():
            id = self.target_id
            url = "/api/v2.0/iscsi/target/id/" + str(id)
            payload = False  # Don't force delete
            response = self.api_connection.delete(url, data=payload)
            log.info(
                f"Deleteing target {self.name} id: {self.target_id} good response {response}"
            )
            return response
        else:
            log.info(f"Target {self.name} does not exist")

    def create_dataset(self):
        url = "/api/v2.0/pool/dataset"
        payload = {
            "name": self.parent + "/" + self.name,
            "type": "FILESYSTEM",
            "compression": "OFF",
            "atime": "OFF",
            "deduplication": "OFF",
            "readonly": "OFF",
            "exec": "OFF",
        }
        response = self.api_connection.post(url, data=payload)
        log.info(f"Creating dataset {self.name} good response {response.ok}")
        return response.ok

    def create_dataset_snapshot(self, snapshot_name):
        url = "/api/v2.0/zfs/snapshot"
        payload = {
            "dataset": self.parent + "/" + self.name,
            "name": snapshot_name,
            "recursive": False,
            "properties": {},
        }
        response = self.api_connection.post(url, data=payload)
        log.info(
            f"Creating dataset snapshot {self.name}@{snapshot_name} good response {response.ok}"
        )
        return response.ok

    def clone_dataset(self):
        url = "/api/v2.0/zfs/snapshot/clone"
        payload = {
            "snapshot": self.parent
            + "/"
            + self.clone_from_dataset
            + "@"
            + self.clone_from_snapshot,
            "dataset_dst": self.parent + "/" + self.name,
        }
        response = self.api_connection.post(url, data=payload)
        log.info(
            f"Cloning dataset {self.parent}/{self.name} from {self.clone_from_dataset}/{self.clone_from_snapshot}"
        )
        return response.ok

    def delete_dataset_snapshot(self, snapshot_name):
        url = (
            "/api/v2.0/zfs/snapshot/id/"
            + self.parent
            + "%2F"
            + self.name
            + "@"
            + snapshot_name
        )
        payload = {}
        response = self.api_connection.delete(url, data=payload)
        log.info(f"Delete dataset snapshot {self.parent}/{self.name}@{snapshot_name}")
        return response

    def delete_dataset(self):
        if self.dataset_exists():
            url = "/api/v2.0/pool/dataset/id/" + self.parent + "%2F" + self.name
            payload = {"recursive": True, "force": True}
            result = self.api_connection.delete(url, data=payload)
            log.info(f"Delete dataset {self.name}")
            return result
        else:
            log.info(f"Dataset {self.name} does not exist")
            return False

    def dataset_exists(self):
        url = "/api/v2.0/pool/dataset?name=" + self.parent + "/" + self.name
        result = self.api_connection.get(url)
        if len(result.json()) == 1:  # We should only get one result on the query
            log.info(f"Dataset {self.name} exists")
            return True
        else:
            log.info(f"Dataset {self.name} does not exists")
            return False

    def create_extent(self, size: int = 0):
        url = "/api/v2.0/iscsi/extent"
        path = "/mnt/" + self.parent + "/" + self.name + "/"
        if self.extent_file is None:
            path = path + self.name
        else:
            path = path + self.extent_file

        payload = {
            "name": self.name,
            "type": "FILE",
            "path": path,
            "filesize": size,
            "blocksize": self.blocksize,
            "pblocksize": False,
            "avail_threshold": None,
            "insecure_tpc": True,
            "xen": False,
            "rpm": "SSD",
            "ro": False,
            "enabled": True,
        }
        response = self.api_connection.post(url, data=payload)
        if response.ok:
            self.extent_id = response.json()["id"]
        log.info(f"Create extent {self.name} at {path}")
        return response.ok

    def delete_extent(self):
        if self.extent_exists():  # Make sure extent exists
            url = "/api/v2.0/iscsi/extent/id/" + str(self.extent_id)
            payload = {}
            result = self.api_connection.delete(url, data=payload)
            log.info(f"Delete extent {self.name} good response {result}")
            return result
        else:
            log.info(f"Extent {self.name} does not exist")

    def extent_exists(self):
        url = "/api/v2.0/iscsi/extent?name=" + self.name

        response = self.api_connection.get(url)

        exists = False
        for response_item in response.json():
            if response_item["name"] == self.name:
                exists = True
                self.extent_id = response_item["id"]
        log.info(f"Extent {self.name} exists {exists}")
        return exists

    def create_target_extent(self):
        url = "/api/v2.0/iscsi/targetextent"

        # Make sure we have extent and target populated
        self.extent_exists()
        self.target_exists()

        if self.target_id is not None or self.extent_id is not None:
            payload = {"target": self.target_id, "extent": self.extent_id}
            response = self.api_connection.post(url, data=payload)
            if response.ok:
                self.extent_target_id = response.json()["id"]
                log.info(
                    f"Create target extent with target_id: {self.target_id}, extent_id: {self.extent_id}"
                )
            return response.ok
        else:
            log.info(f"Extent or Target do not exist for {self.name}")
            return False

    def delete_target_extent(self):
        if self.target_extent_exists():
            url = "/api/v2.0/iscsi/targetextent/id/" + str(self.extent_target_id)
            payload = False  # Don't force
            result = self.api_connection.delete(url, data=payload)
            log.info(
                f"Delete target extent {self.name} with id {self.extent_target_id}"
            )
            return result
        else:
            log.info(f"Extent Target does not exist for {self.name}")
            return False

    def target_extent_exists(self):
        if self.target_id is None:
            if not self.target_exists():
                log.info(
                    f"Target does not exist for {self.name} with id {self.target_id}"
                )
                return False
        if self.extent_id is None:
            if not self.extent_exists():
                log.info(
                    f"Extent does not exist for {self.name} with id {self.extent_id}"
                )
                return False

        url = (
            "/api/v2.0/iscsi/targetextent?target="
            + str(self.target_id)
            + "&extent="
            + str(self.extent_id)
        )
        response = self.api_connection.get(url)
        if response.ok:
            # Assuming there will always be a single item in the response, [0]
            if len(response.json()) > 0:
                self.extent_target_id = response.json()[0]["id"]
                log.info(
                    f"Target Extent {self.name} exists with id: {self.extent_target_id}"
                )
                return True
        else:
            log.info(f"Target Extent {self.name} does not exist")
            return False
