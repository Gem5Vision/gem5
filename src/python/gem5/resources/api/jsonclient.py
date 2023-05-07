import json
from pathlib import Path
from m5 import defines
import urllib.request
import urllib.parse
import requests
from m5.util import warn, fatal
from client import AbstractClient


class JSONClient(AbstractClient):
    def __init__(self, path: str):
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

    def get_resource_obj(self, resource_id, resource_version=None) -> dict:
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
            fatal(f"Resource with ID '{resource_id}' not found.")
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