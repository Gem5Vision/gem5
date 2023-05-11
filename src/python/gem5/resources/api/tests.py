import os
import unittest
from unittest import mock
from unittest.mock import patch
from . import client_wrapper
from .jsonclient import JSONClient
from .mongoclient import MongoClient
from _m5.core import gem5Version
""" resource_id = "x86-ubuntu-18.04-img"
version = "1.1.0"

print(get_resource_obj(resource_id, version))
print(get_resource_obj(resource_id, version, "atharav")) """

mock_config = {
    "schemaUrl": "https://raw.githubusercontent.com/Gem5Vision/json-to-mongodb/main/schema/schema.json",
    "resources": {
        "baba": {
            "url": "src/python/gem5/resources/api/refs/test.json",
            "isMongo": False
        }
    }
}

mock_clients = {}
for resource in mock_config["resources"]:
    database = mock_config["resources"][resource]
    if database["isMongo"]:
        mock_clients[resource] = MongoClient(
            database["uri"], database["database"], database["collection"]
        )
    else:
        mock_clients[resource] = JSONClient(database["url"])


@patch('src.python.gem5.resources.api.client_wrapper.config', mock_config)
@patch('src.python.gem5.resources.api.client_wrapper.clients', mock_clients)
# @patch('src.python.m5.defines.gem5Version', "24.0")
class Test(unittest.TestCase):
    def test_config(self):
        """Ensure the config is set correctly."""
        print(client_wrapper.config)
        print(client_wrapper.clients)
        print(client_wrapper.get_resource_obj(
            "kernel-example", "1.0.0", "baba"))
        print(gem5Version)
