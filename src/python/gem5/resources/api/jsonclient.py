import json
from pathlib import Path
from m5 import defines
import urllib.request
import urllib.parse
import requests
from m5.util import warn, fatal


def fatal(msg):
    print("FATAL: ")
    print(msg)
    exit(1)


def warn(msg):
    print("WARNING: ")
    print(msg)


class JSONClient:
    def __init__(self, path: str):
        self.path = path
        self.resources = []

        if Path(self.path).is_file():
            self.resources = json.load(open(self.path))
        elif not self.__url_validator(self.path):
            raise Exception(
                f"Resources location '{self.path}' is not a valid path or URL."
            )
        else:
            self.resources = requests.get(self.path).json()

    def __url_validator(self, url):
        try:
            result = urllib.parse.urlparse(url)
            return all([result.scheme, result.netloc, result.path])
        except:
            return False

    def get_resource_obj(self, resource_id, resource_version=None) -> dict:
        """
        :param resource_id: The id of the resource.
        :optional param resource_version: The version of the resource.
        If not given, the latest version compatible with current gem5 version is returned.
        :return: The resource as a Python dictionary.
        """
        # getting all the resources with the given id from MongoDB
        resources = [
            resource for resource in self.resources if resource["id"] == resource_id]
        # if no resource with the given id is found throw an exception
        if len(resources) == 0:
            fatal(f"Resource with ID '{resource_id}' not found.")
        # sorting the resources by version
        resources.sort(key=lambda x: list(map(
            int, x["resource_version"].split('.'))), reverse=True)

        # if a version is given, search for the resource with the given version
        if resource_version:
            return self.__search_version(resources, resource_version)

        # if no version is given, return the compatible resource with the latest version
        return self.__get_compatible_resources(resources)[0]

    def __search_version(self, resources, resource_version) -> dict:
        """Searches for the resource with the given version. If the resource is not found, throws an exception."""
        for resource in resources:
            if resource["resource_version"] == resource_version:
                if defines.gem5Version not in resource["gem5_versions"]:
                    warn(
                        f"Resource compatible with gem5 version: '{defines.gem5Version}' not found.\n"
                        "Resource versions can be found at: "
                        f"https://gem5vision.github.io/gem5-resources-website/resources/{resources[0]['id']}/versions")
                return resource
        fatal(
            f"Resource {resources[0]['id']} with version '{resource_version}' not found.\nResource "
            "versions can be found at: "
            f"https://gem5vision.github.io/gem5-resources-website/resources/{resources[0]['id']}/versions")

    def __get_compatible_resources(self, resources) -> list:
        """Returns the compatible resources with the given gem5 version."""
        compatible_resources = []
        for resource in resources:
            if defines.gem5Version in resource["gem5_versions"]:
                compatible_resources.append(resource)

        if len(compatible_resources) == 0:
            warn(
                f"Resource compatible with gem5 version: '{defines.gem5Version}' not found.\n"
                "Resource versions can be found at: "
                f"https://gem5vision.github.io/gem5-resources-website/resources/{resources[0]['id']}/versions")
            return resources
        return compatible_resources
