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


from typing import Optional, Dict
import json
from pathlib import Path
from typing import Optional, Dict, List
from .client_api.jsonclient import JSONClient
from .client_api.mongoclient import MongoClient
from python.gem5 import __file__
import os


def create_clients(
    config: Dict,
) -> Dict:
    """
    This function creates respective client object for each database in the config file according to the type of database.
    Params: config: config file containing the database information
    Returns: clients: dictionary of clients for each database
    """
    clients = {}
    for client in config["sources"]:
        database = config["sources"][client]
        if database["isMongo"]:
            clients[client] = MongoClient(database)
        else:
            clients[client] = JSONClient(database["url"])
    return clients


clients = None

# First check if the config file path is provided in the environment variable
if "GEM5_RESOURCES_CONFIG" in os.environ:
    config_file_path = Path(os.environ["GEM5_RESOURCES_CONFIG"])
# If not, check if the config file is present in the current directory
elif (Path().resolve() / "gem5-config.json").exists():
    config_file_path = Path().resolve() / "gem5-config.json"
# If not, use the default config in the build directory
else:
    config_file_path = (
        Path(__file__).resolve().parent.parent / "gem5-config.json"
    )

# If config file is found, load the config file
if config_file_path.exists():
    with open(config_file_path, "r") as file:
        config = json.load(file)
else:
    raise Exception(f"Config file not found at {config_file_path}")

# If clients is not already created, create clients for each database
if clients is None:
    clients = create_clients(config)


def get_resource_json_obj(
    resource_id,
    resource_version: Optional[str] = None,
    databases: Optional[List[str]] = [],
) -> Dict:
    """
    This function returns the resource object from the corresponding database.

    :param resource_id: resource id of the resource
    :optional param resource_version: resource version of the resource
    :optional param database: database name. If not provided, the first database in the config file is used
    :return: resource object
    """
    resources = []
    if not databases:
        databases = list(clients.keys())
    for database in databases:
        if database not in clients:
            raise Exception(f"Database: {database} does not exist")
        resource = clients[database].get_resource_json_obj_from_client(
            resource_id, resource_version
        )
        if resource is not None:
            resources.append(resource)

    if len(resources) == 0:
        if resource_version is None:
            raise Exception(f"Resource with ID '{resource_id}' not found.")
        else:
            raise Exception(
                f"Resource {resource_id} with version '{resource_version}'"
                " not found.\nResource versions can be found at: "
                f"https://gem5vision.github.io/gem5-resources-website/resources/{resource_id}/versions"
            )
    if len(resources) > 1:
        raise Exception(
            f"Resource: {resource_id} exists in multiple databases. "
            "Please specify the database name to use."
        )

    return resources[0]
