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
import json
from pathlib import Path
from typing import Optional, Dict, Union, Type, Tuple, List


def create_clients(
    config: dict,
):
    """
    This function creates respective client object for each database in the config file according to the type of database.
    Params: config: config file containing the database information
    Returns: clients: dictionary of clients for each database
    """
    clients = {}
    for resource in config["resources"]:
        database = config["resources"][resource]
        if database["isMongo"]:
            clients[resource] = MongoClient(database)
        else:
            clients[resource] = JSONClient(database["url"])
    return clients


clients = None


if clients is None:
    # read gem5/configs/gem5Resources.config.json using pathlib
    # gem5Resources.config.json contains the database information
    config = json.load(
        open(
            Path(__file__).parent.parent.parent.parent.parent.parent.parent
            / "configs/gem5Resources.config.json",
            "r",
        )
    )
    clients = create_clients(config)


def get_resource_obj(
    resource_id,
    resource_version: Optional[str] = None,
    database: Optional[str] = None,
) -> dict:
    """
    This function returns the resource object from the corresponding database.

    :param resource_id: resource id of the resource
    :optional param resource_version: resource version of the resource
    :optional param database: database name. If not provided, the first database in the config file is used
    :return: resource object
    """
    if not database:
        database = list(clients.keys())[0]
    if database not in clients:
        raise Exception(f"Database: {database} does not exist")
    return clients[database].get_resource_obj_from_client(
        resource_id, resource_version
    )
