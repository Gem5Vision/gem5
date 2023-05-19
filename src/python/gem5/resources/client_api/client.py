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

from abc import abstractmethod, ABC
import urllib.request
import urllib.parse
from _m5 import core
import warnings
from typing import Optional, Dict, Union, Type, Tuple, List, Any
from distutils.version import StrictVersion


class AbstractClient(ABC):
    @abstractmethod
    def get_resources_by_id(self, resource_id: str) -> List[Dict[str, Any]]:
        """
        Retrieves all the resources with the given ID.
        :param resource_id: The ID of the Resource.
        :return: A list of resources as Python dictionaries.
        """
        raise NotImplementedError

    def get_resource_json_obj_from_client(
        self, resource_id: str, resource_version: Optional[str] = None
    ) -> dict:
        """
        Retrieves the Resource object identified by the given resource ID.
        :param resource_id: The ID of the Resource.
        :param resource_version: (optional) The version of the Resource.
        If not given, the latest version compatible with the current
        gem5 version is returned.
        """
        # getting all the resources with the given id from the dictionary
        resources = self.get_resources_by_id(resource_id)
        # if no resource with the given id is found throw an exception
        if len(resources) == 0:
            raise Exception(f"Resource with ID '{resource_id}' not found.")
        # sorting the resources by version
        resources = self._sort_resources_by_version(resources)

        # if a version is given, search for the resource with the given version
        if resource_version:
            return self._search_version(resources, resource_version)

        # if no version is given, return the compatible
        # resource with the latest version
        compatible_resources = self._get_compatible_resources(resources)
        if len(compatible_resources) == 0:
            self.check_resource_version_compatibility(resources[0], resource_version)
            return resources[0]
        return compatible_resources[0]

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

    def _search_version(self, resources: List, resource_version: str = "1.0.0") -> dict:
        """
        Searches for the resource with the given version. If the resource is
        not found, an exception is thrown.
        :param resources: A list of resources to search through.
        :param resource_version: The version of the resource to search for.
        :return: The resource object as a Python dictionary if found.
        :raises: RuntimeError if the resource with the specified version is
        not found.
        """
        resource = next(
            iter(
                [
                    resource
                    for resource in resources
                    if resource["resource_version"] == resource_version
                ]
            ),
            None,
        )
        if resource is None:
            raise Exception(
                f"Resource {resources[0]['id']} with version '{resource_version}'"
                " not found.\nResource versions can be found at: "
                f"https://gem5vision.github.io/gem5-resources-website/resources/{resources[0]['id']}/versions"
            )
        self.check_resource_version_compatibility(resource, resource_version)
        return resource

    def _get_compatible_resources(self, resources: List) -> List:
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
            if core.gem5Version in resource["gem5_versions"]
        ]
        return compatible_resources

    def _sort_resources_by_version(self, resources: List) -> List:
        """
        Sorts the resources by version in descending order.
        :param resources: A list of resources to sort.
        :return: A list of sorted resources.
        """
        return sorted(
            resources,
            key=lambda resource: StrictVersion(resource["resource_version"]),
            reverse=True,
        )

    def check_resource_version_compatibility(
        self, resource: dict, gem5_version: str = core.gem5Version
    ) -> bool:
        if gem5_version not in resource["gem5_versions"]:
            warnings.warn(
                f"Resource {resource['id']} version {resource['resource_version']} "
                f"is not known to be compatible with gem5 version {core.gem5Version}. "
                "This may cause problems with your simulation. This resource's compatibility "
                "with different gem5 versions can be found here:"
                "https://gem5vision.github.io/gem5-resources-website"
                f"/resources/{resource['id']}/versions"
            )
            return False
        return True
