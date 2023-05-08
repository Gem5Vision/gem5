import os
import unittest
from .client_wrapper import get_resource_obj

""" resource_id = "x86-ubuntu-18.04-img"
version = "1.1.0"

print(get_resource_obj(resource_id, version))
print(get_resource_obj(resource_id, version, "atharav")) """


class Test(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        """Prior to running the suite we set the resource directory to
        "ref/resource-specialization.json"
        """
        os.environ["GEM5_RESOURCE_JSON"] = os.path.join(
            os.path.realpath(os.path.dirname(__file__)),
            "refs",
            "obtain-resource.json",
        )

    @classmethod
    def tearDownClass(cls) -> None:
        """After running the suite we unset the gem5-resource JSON file, as to
        not interfere with others tests.
        """
        del os.environ["GEM5_RESOURCE_JSON"]

    def get_resource_dir(cls) -> str:
        """To ensure the resources are cached to the same directory as all
        other tests, this function returns the location of the testing
        directories "resources" directory.
        """
        return os.path.join(
            os.path.realpath(os.path.dirname(__file__)),
            os.pardir,
            os.pardir,
            os.pardir,
            "gem5",
            "resources",
        )

    def test_obtain_resources_with_version_incompatible(self):
        resource = None
        with self.assertWarns(Warning) as warning:
            resource = get_resource_obj(resource_id="x86-ubuntu-18.04-img",
                                        resource_version="1.0.0")
        self.assertEqual(f"Resource compatible with gem5 version: '23.1' not found.\n"
                         "Resource versions can be found at: "
                         f"https://gem5vision.github.io/gem5-resources-website/resources/x86-ubuntu-18.04-img/versions", warning.warning.args[0])
