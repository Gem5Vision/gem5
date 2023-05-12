# from pymongo.collection import Collection
from .client import AbstractClient
import requests


class MongoClient(AbstractClient):
    def __init__(self, config):
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

    def __get_resource_by_id(self, resource_id):
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

    def get_resource_obj(self, resource_id, resource_version=None) -> dict:
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
