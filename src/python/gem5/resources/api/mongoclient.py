import pymongo
from .client import AbstractClient


class MongoClient(AbstractClient):
    def __init__(self, uri, db, collection):
        """
        Initializes a connection to a MongoDB database.
        :param uri: The URI for connecting to the MongoDB server.
        :param db: The name of the database to connect to.
        :param collection: The name of the collection within the database.
        """
        self.__client = pymongo.MongoClient(uri)
        self.__db = self.__client[db]
        self.__collection = self.__db[collection]

    def get_resource_obj(self, resource_id, resource_version=None) -> dict:
        """
        :param resource_id: The ID of the Resource.
        :optional param resource_version: The version of the Resource.
        If not given, the latest version compatible with current gem5 version is returned.
        :return: The Resource as a Python dictionary.
        """
        # getting all the resources with the given ID from MongoDB
        resources = list(
            self.__collection.find({"id": resource_id}, {"_id": 0})
        )
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
