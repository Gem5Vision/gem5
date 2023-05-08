from abc import abstractmethod, ABC
import urllib.request
import urllib.parse
from .m5 import defines
import warnings


class AbstractClient(ABC):
    @abstractmethod
    def get_resource_obj(self, resource_id, resource_version=None) -> dict:
        """
        Retrieves the Resource object identified by the given resource ID.
        :param resource_id: The ID of the Resource.
        :param resource_version: (optional) The version of the Resource.
        If not given, the latest version compatible with the current
        gem5 version is returned.
        """

    def _url_validator(self, url):
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

    def _search_version(self, resources, resource_version) -> dict:
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
                if defines.gem5Version not in resource["gem5_versions"]:
                    warnings.warn(
                        f"Resource compatible with gem5 version: '{defines.gem5Version}' not found.\n"
                        "Resource versions can be found at: "
                        f"https://gem5vision.github.io/gem5-resources-website/resources/{resources[0]['id']}/versions"
                    )
                return resource
        raise Exception(
            f"Resource {resources[0]['id']} with version '{resource_version}'"
            " not found.\nResource versions can be found at: "
            f"https://gem5vision.github.io/gem5-resources-website/resources/{resources[0]['id']}/versions"
        )

    def _get_compatible_resources(self, resources) -> list:
        """
        Returns a list of compatible resources with the given gem5 version.
        :param resources: A list of resources to filter.
        :return: A list of compatible resources as Python dictionaries.
        If no compatible resources are found, the original list of resources 
        is returned.
        """
        compatible_resources = []
        for resource in resources:
            if defines.gem5Version in resource["gem5_versions"]:
                compatible_resources.append(resource)

        if len(compatible_resources) == 0:
            warnings.warn(
                f"Resource compatible with gem5 version: '{defines.gem5Version}' not found.\n"
                "Resource versions can be found at: "
                f"https://gem5vision.github.io/gem5-resources-website/resources/{resources[0]['id']}/versions"
            )
            return resources
        return compatible_resources
