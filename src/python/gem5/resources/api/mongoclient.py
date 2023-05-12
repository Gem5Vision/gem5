# Copyright (c) 2023 The Regents of the University of California
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

from .client import AbstractClient
import requests
from typing import Optional, Dict, Union, Type, Tuple, List


class MongoClient(AbstractClient):
    def __init__(self, config: Dict[str, str]):
        """
        Initializes a connection to a MongoDB database.
        :param uri: The URI for connecting to the MongoDB server.
        :param db: The name of the database to connect to.
        :param collection: The name of the collection within the database.
        """
        self.apiKey = config["apiKey"]
        self.url = config["url"]
        self.collection = config["collection"]
        self.database = config["database"]
        self.dataSource = config["dataSource"]
        self.name = config["name"]

    def get_token(self):
        token = requests.post(
            f"https://realm.mongodb.com/api/client/v2.0/app/{self.name}/auth/providers/api-key/login",
            json={"key": self.apiKey},
        )
        return token.json()["access_token"]

    def __get_resource_by_id(self, resource_id: str) -> List[Dict]:
        resources = requests.post(
            f"{self.url}/action/find",
            json={
                "dataSource": self.dataSource,
                "collection": self.collection,
                "database": self.database,
                "filter": {"id": resource_id},
            },
            headers={"Authorization": f"Bearer {self.get_token()}"},
        )
        return resources.json()["documents"]

    def get_resource_obj(
        self,
        resource_id: str,
        resource_version: Optional[str] = None,
    ) -> Dict:
        """
        :param resource_id: The ID of the Resource.
        :optional param resource_version: The version of the Resource.
        If not given, the latest version compatible with current gem5 version is returned.
        :return: The Resource as a Python dictionary.
        """
        # getting all the resources with the given ID from MongoDB
        resources = list(self.__get_resource_by_id(resource_id))
        # if no resource with the given ID is found throw an Exception
        if len(resources) == 0:
            raise Exception(f"Resource with ID '{resource_id}' not found.")
        # sorting the resources by version
        resources.sort(
            key=lambda x: list(map(int, x["resource_version"].split("."))),
            reverse=True,
        )

        # if a version is given, search for the resource with the given version
        if resource_version:
            return self._search_version(resources, resource_version)

        # if no version is given, return the compatible resource with the latest version
        return self._get_compatible_resources(resources)[0]
