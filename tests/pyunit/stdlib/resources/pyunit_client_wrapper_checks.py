# Copyright (c) 2022 The Regents of the University of California
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are
# met: redistributions of source code must retain the above copyright
# notice, this list of conditions and the following disclaimer;
# redistributions in binary form must reproduce the above copyright
# notice, this list of conditions and the following disclaimer in the
# documentation and/or other materials provided with the distribution;
# neither the name of the copyright holders nor the names of its
# contributors may be used to endorse or promote products derived from
# this software without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
# "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
# LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR
# A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT
# OWNER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL,
# SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT
# LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE,
# DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY
# THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
# (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
# OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

import unittest
from gem5.isas import ISA
from python.gem5.resources.api.client_wrapper import (
    get_resource_obj,
    create_clients,
)
from typing import Dict
from unittest.mock import patch
import json

mock_config_json = {
    "schemaUrl": "https://raw.githubusercontent.com/Gem5Vision/json-to-mongodb/main/schema/schema.json",
    "resources": {
        "baba": {
            "url": "tests/pyunit/stdlib/resources/refs/resources.json",
            "isMongo": False,
        }
    },
}

mock_config_mongo = {
    "schemaUrl": "https://raw.githubusercontent.com/Gem5Vision/json-to-mongodb/main/schema/schema.json",
    "resources": {
        "gem5-resources": {
            "dataSource": "gem5-vision",
            "database": "gem5-vision",
            "collection": "resources",
            "url": "https://data.mongodb-api.com/app/data-ejhjf/endpoint/data/v1",
            "name": "data-ejhjf",
            "apiKey": "OIi5bAP7xxIGK782t8ZoiD2BkBGEzMdX3upChf9zdCxHSnMoiTnjI22Yw5kOSgy9",
            "isMongo": True,
        }
    },
}

mock_config_combined = {
    "schemaUrl": "https://raw.githubusercontent.com/Gem5Vision/json-to-mongodb/main/schema/schema.json",
    "resources": {
        "gem5-resources": {
            "dataSource": "gem5-vision",
            "database": "gem5-vision",
            "collection": "resources",
            "url": "https://data.mongodb-api.com/app/data-ejhjf/endpoint/data/v1",
            "name": "data-ejhjf",
            "apiKey": "OIi5bAP7xxIGK782t8ZoiD2BkBGEzMdX3upChf9zdCxHSnMoiTnjI22Yw5kOSgy9",
            "isMongo": True,
        },
        "baba": {
            "url": "tests/pyunit/stdlib/resources/refs/resources.json",
            "isMongo": False,
        },
    },
}

mock_json = {}

with open("tests/pyunit/stdlib/resources/refs/mongo_mock.json", "r") as f:
    mock_json = json.load(f)


def mocked_requests_post(*args, **kwargs):
    class MockResponse:
        def __init__(self, json_data, status_code):
            self.json_data = json_data
            self.status_code = status_code

        def json(self):
            return self.json_data

    if "/api-key/login" in args[0]:
        return MockResponse({"access_token": "test-token"}, 200)
    if "/action/find" in args[0]:
        if "json" in kwargs:
            if kwargs["json"]["filter"]["id"] == "invalid-id":
                return MockResponse(
                    {
                        "documents": [],
                    },
                    200,
                )
        return MockResponse(
            {
                "documents": mock_json,
            },
            200,
        )

    return MockResponse(None, 404)


class ClientWrapperTestSuite(unittest.TestCase):
    @patch("python.gem5.resources.api.client_wrapper.config", mock_config_json)
    @patch(
        "python.gem5.resources.api.client_wrapper.clients",
        create_clients(mock_config_json),
    )
    def test_get_resource_obj(self):
        # Test that the resource object is correctly returned
        resource = "this-is-a-test-resource"
        resource = get_resource_obj(resource)
        self.assertEqual(resource["id"], "this-is-a-test-resource")
        self.assertEqual(resource["resource_version"], "2.0.0")
        self.assertEqual(resource["category"], "binary")
        self.assertEqual(
            resource["description"], "This is a test resource but double newer"
        )
        self.assertEqual(
            resource["source_url"],
            "https://github.com/gem5/gem5-resources/tree/develop/src/asmtest",
        )
        self.assertEqual(resource["architecture"], "X86")

    @patch("python.gem5.resources.api.client_wrapper.config", mock_config_json)
    @patch(
        "python.gem5.resources.api.client_wrapper.clients",
        create_clients(mock_config_json),
    )
    def test_get_resource_obj_invalid_database(self):
        # Test that an exception is raised when an invalid database is passed
        resource_id = "test-id"
        database = "invalid"
        with self.assertRaises(Exception) as context:
            get_resource_obj(resource_id, database=database)
        self.assertTrue(
            f"Database: {database} does not exist" in str(context.exception)
        )

    @patch("python.gem5.resources.api.client_wrapper.config", mock_config_json)
    @patch(
        "python.gem5.resources.api.client_wrapper.clients",
        create_clients(mock_config_json),
    )
    def test_get_resource_obj_with_version(self):
        # Test that the resource object is correctly returned
        resource_id = "this-is-a-test-resource"
        resource_version = "1.0.0"
        resource = get_resource_obj(
            resource_id, resource_version=resource_version
        )
        self.assertEqual(resource["id"], "this-is-a-test-resource")
        self.assertEqual(resource["resource_version"], "1.0.0")
        self.assertEqual(resource["category"], "binary")
        self.assertEqual(resource["description"], "This is a test resource")
        self.assertEqual(
            resource["source_url"],
            "https://github.com/gem5/gem5-resources/tree/develop/src/asmtest",
        )
        self.assertEqual(resource["architecture"], "X86")

    @patch(
        "python.gem5.resources.api.client_wrapper.config", mock_config_mongo
    )
    @patch(
        "python.gem5.resources.api.client_wrapper.clients",
        create_clients(mock_config_mongo),
    )
    @patch("requests.post", side_effect=mocked_requests_post)
    def test_get_resource_obj(self, mock_get):
        resource = "x86-ubuntu-18.04-img"
        resource = get_resource_obj(resource, database="gem5-resources")
        self.assertEqual(resource["id"], "x86-ubuntu-18.04-img")
        self.assertEqual(resource["resource_version"], "2.0.0")
        self.assertEqual(resource["category"], "diskimage")
        self.assertEqual(
            resource["description"],
            "A disk image containing Ubuntu 18.04 for x86. This image will run an `m5 readfile` instruction after booting. If no script file is specified an `m5 exit` instruction will be executed.",
        )
        self.assertEqual(
            resource["source_url"],
            "https://github.com/gem5/gem5-resources/tree/develop/src/x86-ubuntu",
        )
        self.assertEqual(resource["architecture"], "X86")

    @patch(
        "python.gem5.resources.api.client_wrapper.config", mock_config_mongo
    )
    @patch(
        "python.gem5.resources.api.client_wrapper.clients",
        create_clients(mock_config_mongo),
    )
    @patch("requests.post", side_effect=mocked_requests_post)
    def test_get_resource_obj_with_version_mongodb(self, mock_get):
        # Test that the resource object is correctly returned
        resource_id = "x86-ubuntu-18.04-img"
        resource_version = "1.0.0"
        resource = get_resource_obj(
            resource_id,
            resource_version=resource_version,
            database="gem5-resources",
        )
        self.assertEqual(resource["id"], "x86-ubuntu-18.04-img")
        self.assertEqual(resource["resource_version"], "1.0.0")
        self.assertEqual(resource["category"], "diskimage")
        self.assertEqual(resource["description"], "This is a test resource")
        self.assertEqual(
            resource["source_url"],
            "https://github.com/gem5/gem5-resources/tree/develop/src/x86-ubuntu",
        )
        self.assertEqual(resource["architecture"], "X86")

    @patch(
        "python.gem5.resources.api.client_wrapper.config", mock_config_mongo
    )
    @patch(
        "python.gem5.resources.api.client_wrapper.clients",
        create_clients(mock_config_mongo),
    )
    @patch("requests.post", side_effect=mocked_requests_post)
    def test_get_resource_obj_with_id_invalid_mongodb(self, mock_get):
        resource_id = "invalid-id"
        with self.assertRaises(Exception) as context:
            get_resource_obj(resource_id, database="gem5-resources")
        self.assertTrue(
            "Resource with ID 'invalid-id' not found."
            in str(context.exception)
        )

    @patch(
        "python.gem5.resources.api.client_wrapper.config", mock_config_mongo
    )
    @patch(
        "python.gem5.resources.api.client_wrapper.clients",
        create_clients(mock_config_mongo),
    )
    @patch("requests.post", side_effect=mocked_requests_post)
    def test_get_resource_obj_with_version_invalid_mongodb(self, mock_get):
        resource_id = "x86-ubuntu-18.04-img"
        resource_version = "2.5.0"
        with self.assertRaises(Exception) as context:
            get_resource_obj(
                resource_id,
                resource_version=resource_version,
                database="gem5-resources",
            )
        self.assertTrue(
            f"Resource x86-ubuntu-18.04-img with version '2.5.0'"
            " not found.\nResource versions can be found at: "
            f"https://gem5vision.github.io/gem5-resources-website/resources/x86-ubuntu-18.04-img/versions"
            in str(context.exception)
        )

    @patch("python.gem5.resources.api.client_wrapper.config", mock_config_json)
    @patch(
        "python.gem5.resources.api.client_wrapper.clients",
        create_clients(mock_config_json),
    )
    def test_get_resource_obj_with_version_invalid_json(self):
        resource_id = "this-is-a-test-resource"
        resource_version = "2.5.0"
        with self.assertRaises(Exception) as context:
            get_resource_obj(
                resource_id,
                resource_version=resource_version,
            )
        self.assertTrue(
            f"Resource this-is-a-test-resource with version '2.5.0'"
            " not found.\nResource versions can be found at: "
            f"https://gem5vision.github.io/gem5-resources-website/resources/this-is-a-test-resource/versions"
            in str(context.exception)
        )

    @patch(
        "python.gem5.resources.api.client_wrapper.config", mock_config_combined
    )
    @patch(
        "python.gem5.resources.api.client_wrapper.clients",
        create_clients(mock_config_combined),
    )
    @patch("requests.post", side_effect=mocked_requests_post)
    def test_get_resource_obj_combine(self, mock_get):
        resource_id_mongo = "x86-ubuntu-18.04-img"
        resource_version_mongo = "1.0.0"
        resource_id_json = "this-is-a-test-resource"
        resource_version_json = "1.0.0"
        resource_mongo = get_resource_obj(
            resource_id_mongo,
            resource_version=resource_version_mongo,
            database="gem5-resources",
        )
        resource_json = get_resource_obj(
            resource_id_json,
            resource_version=resource_version_json,
            database="baba",
        )
        self.assertEqual(resource_mongo["id"], "x86-ubuntu-18.04-img")
        self.assertEqual(resource_mongo["resource_version"], "1.0.0")
        self.assertEqual(resource_mongo["category"], "diskimage")
        self.assertEqual(
            resource_mongo["description"], "This is a test resource"
        )
        self.assertEqual(
            resource_mongo["source_url"],
            "https://github.com/gem5/gem5-resources/tree/develop/src/x86-ubuntu",
        )
        self.assertEqual(resource_mongo["architecture"], "X86")

        self.assertEqual(resource_json["id"], "this-is-a-test-resource")
        self.assertEqual(resource_json["resource_version"], "1.0.0")
        self.assertEqual(resource_json["category"], "binary")
        self.assertEqual(
            resource_json["description"], "This is a test resource"
        )
        self.assertEqual(
            resource_json["source_url"],
            "https://github.com/gem5/gem5-resources/tree/develop/src/asmtest",
        )
        self.assertEqual(resource_json["architecture"], "X86")
