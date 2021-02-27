from pydantic import BaseModel, HttpUrl, BaseSettings
import requests
from requests.auth import HTTPBasicAuth
import json


class freenas_api(BaseSettings):
    url: HttpUrl
    username: str
    password: str

    def auth(self):
        return HTTPBasicAuth(self.username, self.password)

    def get(self, uri) -> bool:
        get_url = self.url + uri
        response = requests.request("GET", get_url, auth=self.auth())
        return response

    def post(self, uri, headers={}, data={}) -> bool:
        post_url = self.url + uri
        response = requests.post(
            url=post_url, auth=self.auth(), headers=headers, data=json.dumps(data)
        )
        return response.ok

    def delete(self, uri, headers={}, data={}) -> bool:
        post_url = self.url + uri
        response = requests.request(
            "DELETE", post_url, headers=headers, data=data, auth=self.auth()
        )
        return response.ok


class iscsi_lun(BaseModel):
    """
    The iqn LUN for iscsi devices
    """

    name: str
    parent: str
    api_connection: freenas_api
    clone_from_snapshot: str = None

    def target_exits(self):
        url = "/api/v2.0/iscsi/target?name=" + self.name
        response = self.api_connection.get(url)
        exists = False
        for response_item in response.json():
            if response_item["name"] == self.name:
                exists = True
        return exists

    def get_target_details(self):
        url = "/api/v2.0/iscsi/target?name=" + self.name
        response = self.api_connection.get(url)
        id = None
        for response_item in response.json():
            if response_item["name"] == self.name:
                id = response_item["id"]
        return id

    def create_target(self, name) -> bool:
        url = "/api/v2.0/iscsi/target"
        payload = {
            "name": name,
            "alias": name,
            "mode": "ISCSI",
            "groups": [
                {"portal": 1, "initiator": 1, "auth": None, "authmethod": "NONE"}
            ],
        }
        return self.api_connection.post(url, data=payload)

    def delete_target(self):
        id = self.get_target_details()
        url = "/api/v2.0/iscsi/target/id/" + str(id)
        payload = "false"  # Don't force delete
        return self.api_connection.delete(url, data=payload)

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
        return self.api_connection.post(url, data=payload)

    def create_dataset_snapshot(self, snapshot_name):
        url = "/api/v2.0/zfs/snapshot"
        payload = {
            "dataset": self.parent + "/" + self.name,
            "name": snapshot_name,
            "recursive": False,
            "properties": {},
        }
        return self.api_connection.post(url, data=payload)

    def clone_dataset(self):
        url = "/api/v2.0/zfs/snapshot/clone"
        payload = {
            "snapshot": self.parent
            + "/"
            + self.clone_from_snapshot
            + "@"
            + self.clone_from_snapshot,
            "dataset_dst": self.parent + "/" + self.name,
        }
        return self.api_connection.post(url, data=payload)

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
        return self.api_connection.delete(url, data=payload)

    def delete_dataset(self):
        url = "/api/v2.0/pool/dataset/id/" + self.parent + "%2F" + self.name
        payload = {}
        return self.api_connection.delete(url, data=payload)

    def dataset_exists(self):
        pass
