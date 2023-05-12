from .jsonclient import JSONClient
from .mongoclient import MongoClient
import json
from pathlib import Path


def create_clients(config):
    clients = {}
    for resource in config["resources"]:
        database = config["resources"][resource]
        if database["isMongo"]:
            clients[resource] = MongoClient(database)
        else:
            clients[resource] = JSONClient(database["url"])
    return clients


# read gem5/configs/gem5Resources.config.json
config = json.load(open("configs/gem5Resources.config.json", "r"))
clients = create_clients(config)


def get_resource_obj(
    resource_id, resource_version=None, database=None
) -> dict:
    if not database:
        database = list(clients.keys())[0]
    if database not in clients:
        raise Exception(f"Database: {database} does not exist")
    return clients[database].get_resource_obj(resource_id, resource_version)
