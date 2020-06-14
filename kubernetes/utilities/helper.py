import requests
import json
import time
import os

password = os.environ['PASSWORD']
server = 'http://shiraz.thesniderpad.com'
username = os.environ['USERNAME']

def freenas_api_get(uri):
    return_text = requests.get(
        server + uri, auth=(username, password)
    ).json()

    return return_text

def freenas_api_delete(uri):
    return_text = requests.delete(
        server + uri, auth=(username, password))

    return return_text

def freenas_api_put(uri, data):
    return_text = requests.put(
        server + uri,
        data,
        auth=(username, password),
        headers={'Content-Type': 'application/json'},
        verify=False,
    )

def freenas_service_restart(service):

    # Disable Service
    dataset_json = {
        'srv_enable': False
    }

    freenas_api_put("/api/v1.0/services/services/" + service + "/", json.dumps(dataset_json))

    # Sleep
    time.sleep(5)

    # Enable Service
    dataset_json = {
        'srv_enable': True
    }

    freenas_api_put("/api/v1.0/services/services/" + service + "/", json.dumps(dataset_json))


def freenas_api_post(uri, data):
    return_text = requests.post(
        server + uri,
        data,
        auth=(username, password),
        headers={'Content-Type': 'application/json'},
        verify=False,
    )

    return return_text

def check_dataset_exists(pool, dataset):
    check = False
    result = freenas_api_get("/api/v1.0/storage/volume/" + pool + "/datasets/")

    i = 0
    while i < len(result):
        if result[i]['name'] == dataset:
            check = True
        i += 1

    return check

def create_dataset(pool, dataset):
    dataset_json = {
        'name': dataset,
        'compression': "off",
    }

    result = freenas_api_post("/api/v1.0/storage/volume/" + pool + "/datasets/", json.dumps(dataset_json))
    if result.ok:
        print("Dataset Create: " + dataset + " on pool: " + pool)

def delete_dataset(pool, dataset):
    # VERY DANGEROUS!!!
    result = freenas_api_delete("/api/v1.0/storage/volume/" + pool + "/datasets/" + dataset)
    if result.ok:
        print("Dataset " + dataset + " on " + pool + " deleted")
    else:
        print("Dataset " + dataset + " on " + pool + " failed")

def check_iscsi_target_exists(target_name):
    check = False
    result = freenas_api_get("/api/v1.0/services/iscsi/target/")

    i = 0
    while i < len(result):
        if result[i]['iscsi_target_name'] == target_name:
            check = True
        i += 1

    return check

def create_iscsi_target(target_name):
    target = {
        'iscsi_target_name': target_name,
        'iscsi_target_alias': target_name,
    }

    result = freenas_api_post("/api/v1.0/services/iscsi/target/", json.dumps(target))
    if result.ok:
        print("Target Created:" + target_name)

    #Now setup the groups
    target_id = get_target_id(target_name)

    target_group = {
        'iscsi_target': target_id,
        'iscsi_target_authgroup': None,
        'iscsi_target_authtype': "None",
        'iscsi_target_initialdigest': "Auto",
        'iscsi_target_initiatorgroup': 1,
        'iscsi_target_portalgroup': 1,
    }
    result = freenas_api_post("/api/v1.0/services/iscsi/targetgroup/", json.dumps(target_group))
    if result.ok:
        print("Target groups created: " + target_name)

def check_iscsi_extent_exists(target_name):
    check = False
    result = freenas_api_get("/api/v1.0/services/iscsi/extent/")

    i = 0
    while i < len(result):
        if result[i]['iscsi_target_extent_name'] == target_name:
            check = True
        i += 1

    return check

def create_iscsi_extent(target_name, pool, dataset, filename):

    extent = {
        'iscsi_target_extent_type': "File",
        'iscsi_target_extent_name': target_name,
        'iscsi_target_extent_filesize': "0",
        'iscsi_target_extent_path': "/mnt/" + pool + "/" + dataset + "/" + filename
    }

    result = freenas_api_post("/api/v1.0/services/iscsi/extent/", json.dumps(extent))
    if result.ok:
        print("Extent Created: " + target_name)

def delete_target(target_name):
    # VERY DANGEROUS!!!

    #Get the target id
    targets = freenas_api_get('/api/v1.0/services/iscsi/target/')

    # Find the target id for the target name
    i = 0
    while i < len(targets):
        if targets[i]['iscsi_target_name'] == target_name:
            target_id = targets[i]['id']
            result = freenas_api_delete('/api/v1.0/services/iscsi/target/' + str(target_id))
            if result.ok:
                print("target " + target_name + " with id " + str(target_id) + " deleted")
            else:
                print("target " + target_name + " with id " + str(target_id) + " failed")
        i+=1

def delete_extent(target_name):
    # VERY DANGEROUS!!!

    #Get the extent id
    extents = freenas_api_get('/api/v1.0/services/iscsi/extent/')

    # Find the extent id for the target name
    i = 0
    while i < len(extents):
        if extents[i]['iscsi_target_extent_name'] == target_name:
            extent_id = extents[i]['id']
            result = freenas_api_delete('/api/v1.0/services/iscsi/extent/' + str(extent_id))
            if result.ok:
                print("extent " + target_name + " with id " + str(extent_id) + " deleted")
            else:
                print("extent " + target_name + " with id " + str(extent_id) + " failed")
        i+=1

def get_target_id(target_name):
    target_id = None
    result = freenas_api_get("/api/v1.0/services/iscsi/target/")

    i = 0
    while i < len(result):
        if result[i]['iscsi_target_name'] == target_name:
            target_id = result[i]['id']
        i += 1

    return target_id

def get_extent_id(target_name):
    extent_id = None
    result = freenas_api_get("/api/v1.0/services/iscsi/extent/")

    i = 0
    while i < len(result):
        if result[i]['iscsi_target_extent_name'] == target_name:
            extent_id = result[i]['id']
        i += 1

    return extent_id

def check_iscsi_target_to_extent_exists(target_name):
    check = False
    result = freenas_api_get("/api/v1.0/services/iscsi/targettoextent/")

    # Get the target id's, if they don't exist, there can't be a match, so just exit
    extent_id = get_extent_id(target_name)
    if extent_id is None:
        return check
    target_id = get_target_id(target_name)
    if target_id is None:
        return check

    i = 0
    while i < len(result):
        if result[i]['iscsi_extent'] == extent_id and result[i]['iscsi_target'] == target_id:
            check = True
        i += 1

    return check

def create_iscsi_target_to_extent(target_name):

    # Get the target id's, if they don't exist, there can't be a match, so just exit
    extent_id = get_extent_id(target_name)
    if extent_id is None:
        return None
    target_id = get_target_id(target_name)
    if target_id is None:
        return None

    target_to_extent = {
        'iscsi_target': target_id,
        'iscsi_extent': extent_id,
        'iscsi_lunid': 0,
    }

    result = freenas_api_post("/api/v1.0/services/iscsi/targettoextent/", json.dumps(target_to_extent))
    if result.ok:
        print("Target to Extent Created: " + target_name)

def delete_target_to_extent(target_name):
    # VERY DANGEROUS!!!

    target_to_extent_id = False
    result = freenas_api_get("/api/v1.0/services/iscsi/targettoextent/")

    # Get the target id's, if they don't exist, there can't be a match, so just exit
    extent_id = get_extent_id(target_name)
    if extent_id is None:
        return target_to_extent_id
    target_id = get_target_id(target_name)
    if target_id is None:
        return target_to_extent_id

    # Find the target to extent mapping
    i = 0
    while i < len(result):
        if result[i]['iscsi_extent'] == extent_id and result[i]['iscsi_target'] == target_id:
            target_to_extent_id = result[i]['id']
            delete_result = freenas_api_delete('/api/v1.0/services/iscsi/targettoextent/' + str(target_to_extent_id))
            if delete_result.ok:
                print("target to extent " + target_name + " with id " + str(target_to_extent_id) + " deleted")
            else:
                print("target to extent " + target_name + " with id " + str(target_to_extent_id) + " failed")
        i += 1

def get_pools():
    result = freenas_api_get("/api/v1.0/storage/volume/")
    return result

def create_snapshot(pool, dataset, key):
    snapshot = {
        'dataset': pool + "/" + dataset,
        'name': key,
    }
    result = freenas_api_post("/api/v1.0/storage/snapshot/", json.dumps(snapshot))
    if result.ok:
        print("Snapshot created: " + pool + "/" + dataset + "@" + key)

def get_snapshots():
    result = freenas_api_get("/api/v1.0/storage/snapshot/")
    return result

def check_snapshot_exists(snapshot_name, filesystem):
    exists = False
    snapshots = get_snapshots()
    for snapshot in snapshots:
        if snapshot['name'] == snapshot_name and snapshot['filesystem'] == filesystem:
            exists = True
    return exists

def get_snapshot_id(snapshot_name, filesystem):
    id = None
    snapshots = get_snapshots()
    for snapshot in snapshots:
        if snapshot['name'] == snapshot_name and snapshot['filesystem'] == filesystem:
            id = snapshot['id']
    return id

def delete_snapshot(snapshot_id):
    result = freenas_api_delete("/api/v1.0/storage/snapshot/" + snapshot_id)
    if result.ok:
        print("Snapshot Deleted " + snapshot_id)

def replicate_snapshot(source, destination):
    #TODO write this function
    print("something")
    data = {

    }
    result = freenas_api_post('/api/v1.0/storage/replication/', data)
