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
    def test_get_resource_obj(self):
        resource = "x86-ubuntu-18.04-img"
        resource = get_resource_obj(resource, database="gem5-resources")
        self.assertEqual(resource["id"], "x86-ubuntu-18.04-img")
        self.assertEqual(resource["resource_version"], "1.0.0")
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
