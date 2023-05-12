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

import json
from pathlib import Path
import requests
from .client import AbstractClient
from typing import Optional, Dict, Union, Type, Tuple, List


class JSONClient(AbstractClient):
    def __init__(
        self, 
        path: str
    ):
        """
        Initializes a JSON database.
        :param path: The path to the Resource, either URL or local.
        """
        self.path = path
        self.resources = []

        if Path(self.path).is_file():
            self.resources = json.load(open(self.path))
        elif not self._url_validator(self.path):
            raise Exception(
                f"Resources location '{self.path}' is not a valid path or URL."
            )
        else:
            self.resources = requests.get(self.path).json()

    def get_resource_obj(
        self, 
        resource_id: str, 
        resource_version: Optional[str] = None
    ) -> Dict[str, Union[str, Dict[str, str], List[str]]]:
        """
        :param resource_id: The ID of the Resource.
        :optional param resource_version: The version of the Resource.
        If not given, the latest version compatible with current gem5 version is returned.
        :return: The Resource as a Python dictionary.
        """
        # getting all the resources with the given id from MongoDB
        resources = [
            resource
            for resource in self.resources
            if resource["id"] == resource_id
        ]
        # if no resource with the given id is found throw an exception
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
