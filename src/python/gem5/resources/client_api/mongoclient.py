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

from urllib import request, parse
from typing import Optional, Dict, Union, Type, Tuple, List, Any
import json


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
        url = (
            "https://realm.mongodb.com/api/client/v2.0/app/"
            f"{self.name}/auth/providers/api-key/login"
        )
        data = {"key": self.apiKey}
        data = json.dumps(data).encode("utf-8")

        req = request.Request(
            url, data=data, headers={"Content-Type": "application/json"}
        )
        response = request.urlopen(req)
        result = json.loads(response.read().decode("utf-8"))
        token = result["access_token"]

        return token

    def get_resources_by_id(self, resource_id: str) -> List[Dict[str, Any]]:
        url = f"{self.url}/action/find"
        data = {
            "dataSource": self.dataSource,
            "collection": self.collection,
            "database": self.database,
            "filter": {"id": resource_id},
        }
        data = json.dumps(data).encode("utf-8")

        headers = {
            "Authorization": f"Bearer {self.get_token()}",
            "Content-Type": "application/json",
        }

        req = request.Request(url, data=data, headers=headers)
        response = request.urlopen(req)
        result = json.loads(response.read().decode("utf-8"))
        resources = result["documents"]

        return resources
