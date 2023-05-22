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


import json
from pathlib import Path
from python.gem5 import __file__
import os
from typing import Optional, Dict, List
from .client_api.client import ClientWrapper

# First check if the config file path is provided in the environment variable
if "GEM5_CONFIG" in os.environ:
    config_file_path = Path(os.environ["GEM5_CONFIG"])
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

clientwrapper = ClientWrapper(config)


def get_resource_json_obj(
    resource_id,
    resource_version: Optional[str] = None,
    clients: Optional[List[str]] = None,
) -> Dict:
    return clientwrapper.get_resource_json_obj_from_client(
        resource_id, resource_version, clients
    )
