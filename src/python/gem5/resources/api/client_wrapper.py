from .jsonclient import JSONClient
from .mongoclient import MongoClient
import json
from pathlib import Path

# read config.json
config = json.load(open(Path(__file__).parent / "config.json"))
clients = {}
for resource in config["resources"]:
    database = config["resources"][resource]
    if database["isMongo"]:
        clients[resource] = MongoClient(
            database["uri"], database["database"], database["collection"]
        )
    else:
        clients[resource] = JSONClient(database["url"])


def get_resource_obj(
    resource_id, resource_version=None, database=None
) -> dict:
    if not database:
        database = list(clients.keys())[0]
    return clients[database].get_resource_obj(resource_id, resource_version)
