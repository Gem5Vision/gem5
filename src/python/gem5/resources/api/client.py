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
from typing import Optional, Dict, Union, Type, Tuple, List


class AbstractClient(ABC):
    @abstractmethod
    def get_resource_obj(
        self, resource_id: str, resource_version: Optional[str] = None
    ) -> dict:
        """
        Retrieves the Resource object identified by the given resource ID.
        :param resource_id: The ID of the Resource.
        :param resource_version: (optional) The version of the Resource.
        If not given, the latest version compatible with the current
        gem5 version is returned.
        """
        raise NotImplementedError

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

    def _search_version(self, resources: List, resource_version: str) -> dict:
        """
        Searches for the resource with the given version. If the resource is
        not found, an exception is thrown.
        :param resources: A list of resources to search through.
        :param resource_version: The version of the resource to search for.
        :return: The resource object as a Python dictionary if found.
        :raises: RuntimeError if the resource with the specified version is not found.
        """
        for resource in resources:
            if resource["resource_version"] == resource_version:
                if core.gem5Version not in resource["gem5_versions"]:
                    warnings.warn(
                        f"Resource compatible with gem5 version: '{core.gem5Version}' not found.\n"
                        "Resource versions can be found at: "
                        f"https://gem5vision.github.io/gem5-resources-website/resources/{resources[0]['id']}/versions"
                    )
                return resource
        raise Exception(
            f"Resource {resources[0]['id']} with version '{resource_version}'"
            " not found.\nResource versions can be found at: "
            f"https://gem5vision.github.io/gem5-resources-website/resources/{resources[0]['id']}/versions"
        )

    def _get_compatible_resources(self, resources: List) -> List:
        """
        Returns a list of compatible resources with the given gem5 version.
        :param resources: A list of resources to filter.
        :return: A list of compatible resources as Python dictionaries.
        If no compatible resources are found, the original list of resources
        is returned.
        """
        compatible_resources = []
        for resource in resources:
            if core.gem5Version in resource["gem5_versions"]:
                compatible_resources.append(resource)

        if len(compatible_resources) == 0:
            warnings.warn(
                f"Resource compatible with gem5 version: '{core.gem5Version}' not found.\n"
                "Resource versions can be found at: "
                f"https://gem5vision.github.io/gem5-resources-website/resources/{resources[0]['id']}/versions"
            )
            return resources
        return compatible_resources
