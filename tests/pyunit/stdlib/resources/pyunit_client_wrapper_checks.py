# Copyright (c) 2022 The Regents of the University of California
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

import unittest
from gem5.resources.api.client_wrapper import get_resource_obj
from gem5.resources.api.client_wrapper import clients
from typing import Dict
from unittest import mock


@mock.patch('gem5.resources.api.client_wrapper.config', {
    "schemaUrl": "https://raw.githubusercontent.com/Gem5Vision/json-to-mongodb/main/schema/schema.json",
    "resources": {
        "gem5-resources": {
            "database": "gem5-vision",
            "collection": "resources",
            "uri": "mongodb+srv://gem5_user:gem5_user@gem5-vision.wp3weei.mongodb.net/?retryWrites=true&w=majority",
            "isMongo": True
        },
        "baba": {
            "url": "https://raw.githubusercontent.com/Gem5Vision/json-to-mongodb/main/kiwi1.json",
            "isMongo": False
        }
    }
})
class ClientWrapperTestSuite(unittest.TestCase):
    pass
