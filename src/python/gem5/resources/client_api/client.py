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

from .jsonclient import JSONClient
from .mongoclient import MongoClient
from python.gem5 import __file__
import urllib.request
import urllib.parse
from _m5 import core
import warnings
from typing import Optional, Dict, List
from distutils.version import StrictVersion


class ClientWrapper:
    def __init__(self, config):
        self.clients = self.create_clients(config)

    def create_clients(
        self,
        config: Dict,
    ) -> Dict:
        """
        This function creates respective client object for each source in the
        config file according to the type of source.
        Params: config: config file containing the source information
        Returns: clients: dictionary of clients for each source
        """
        clients = {}
        for client in config["sources"]:
            client_source = config["sources"][client]
            if client_source["isMongo"]:
                clients[client] = MongoClient(client_source)
            else:
                clients[client] = JSONClient(client_source["url"])
        return clients

    def get_all_resources_by_id(
        self,
        resource_id: str,
        clients: Optional[List[str]] = None,
    ):
        resources = []
        if not clients or len(clients) == 0:
            clients = list(self.clients.keys())
        for client in clients:
            if client not in self.clients:
                raise Exception(f"Client: {client} does not exist")
            resources.extend(
                self.clients[client].get_resources_by_id(resource_id)
            )
        # check if no 2 resources have the same id and version
        if len(resources) > 1:
            for i in range(len(resources)):
                for j in range(i + 1, len(resources)):
                    if (
                        resources[i]["resource_version"]
                        == resources[j]["resource_version"]
                    ):
                        raise Exception(
                            f"Resource {resource_id} has multiple resources with"
                            f" the same version: {resources[i]['resource_version']}"
                        )
        return resources

    def get_resource_json_obj_from_client(
        self,
        resource_id: str,
        resource_version: Optional[str] = None,
        clients: Optional[List[str]] = None,
    ) -> Dict:
        # getting all the resources with the given id from the dictionary
        resources = self.get_all_resources_by_id(resource_id, clients)
        # if no resource with the given id is found, return None
        if len(resources) == 0:
            raise Exception(f"Resource with ID '{resource_id}' not found.")

        resource_to_return = None

        if resource_version:
            resource_to_return = self._search_version_in_resources(
                resources, resource_id, resource_version
            )

        else:
            compatible_resources = (
                self._get_resources_compatible_with_gem5_version(resources)
            )
            if len(compatible_resources) == 0:
                resource_to_return = self._sort_resources(resources)[0]
            else:
                resource_to_return = self._sort_resources(
                    compatible_resources
                )[0]

        self._check_resource_version_compatibility(resource_to_return)

        return resource_to_return

    def _url_validator(self, url: str) -> bool:
        """
        Validates the provided URL.
        :param url: The URL to be validated.
        :return: True if the URL is valid, False otherwise.
        """
        try:
            result = urllib.parse.urlparse(url)
            return all([result.scheme, result.netloc, result.path])
        except:
            return False

    def _search_version_in_resources(
        self, resources: List, resource_id: str, resource_version: str
    ) -> Dict:
        """
        Searches for the resource with the given version. If the resource is
        not found, an exception is thrown.
        :param resources: A list of resources to search through.
        :param resource_version: The version of the resource to search for.
        :return: The resource object as a Python dictionary if found.
        If not found, None is returned.
        """
        return_resource = next(
            iter(
                [
                    resource
                    for resource in resources
                    if resource["resource_version"] == resource_version
                ]
            ),
            None,
        )
        if not return_resource:
            raise Exception(
                f"Resource {resource_id} with version '{resource_version}'"
                " not found.\nResource versions can be found at: "
                f"https://gem5vision.github.io/gem5-resources-website/resources/{resource_id}/versions"
            )
        return return_resource

    def _get_resources_compatible_with_gem5_version(
        self, resources: List, gem5_version: str = core.gem5Version
    ) -> List:
        """
        Returns a list of compatible resources with the current gem5 version.
        :param resources: A list of resources to filter.
        :return: A list of compatible resources as Python dictionaries.
        If no compatible resources are found, the original list of resources
        is returned.
        """
        compatible_resources = [
            resource
            for resource in resources
            if gem5_version in resource["gem5_versions"]
        ]
        return compatible_resources

    def _sort_resources(self, resources: List) -> List:
        """
        Sorts the resources by version in descending order.
        :param resources: A list of resources to sort.
        :return: A list of sorted resources.
        """
        return sorted(
            resources,
            key=lambda resource: (
                resource["id"].lower(),
                StrictVersion(resource["resource_version"]),
            ),
            reverse=True,
        )

    def _check_resource_version_compatibility(
        self, resource: dict, gem5_version: str = core.gem5Version
    ) -> bool:
        if not resource:
            return False
        if gem5_version not in resource["gem5_versions"]:
            warnings.warn(
                f"Resource {resource['id']} version {resource['resource_version']} "
                f"is not known to be compatible with gem5 version {gem5_version}. "
                "This may cause problems with your simulation. This resource's compatibility "
                "with different gem5 versions can be found here:"
                "https://gem5vision.github.io/gem5-resources-website"
                f"/resources/{resource['id']}/versions"
            )
            return False
        return True
