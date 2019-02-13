#!/usr/bin/env python
# -*- encoding: utf-8 -*-

# Copyright (c) 2002-2019 "Neo4j,"
# Neo4j Sweden AB [http://neo4j.com]
#
# This file is part of Neo4j.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.


DEFAULT_PORT = 7687

# Connection Pool Management
DEFAULT_MAX_CONNECTION_LIFETIME = 3600  # 1h
DEFAULT_MAX_CONNECTION_POOL_SIZE = 100
DEFAULT_CONNECTION_TIMEOUT = 5.0  # 5s

DEFAULT_KEEP_ALIVE = True

# Connection Settings
DEFAULT_CONNECTION_ACQUISITION_TIMEOUT = 60  # 1m


class ServerInfo(object):

    address = None

    def __init__(self, address, protocol_version):
        self.address = address
        self.protocol_version = protocol_version
        self.metadata = {}

    @property
    def agent(self):
        return self.metadata.get("server")

    def version_info(self):
        if not self.agent:
            return None
        _, _, value = self.agent.partition("/")
        value = value.replace("-", ".").split(".")
        for i, v in enumerate(value):
            try:
                value[i] = int(v)
            except ValueError:
                pass
        return tuple(value)

    def supports(self, feature):
        if not self.agent:
            return None
        if not self.agent.startswith("Neo4j/"):
            return None
        if feature == "bytes":
            return self.version_info() >= (3, 2)
        elif feature == "statement_reuse":
            return self.version_info() >= (3, 2)
        elif feature == "run_metadata":
            return self.protocol_version >= 3
        else:
            return None


from neobolt.impl.python.direct import (
    Connection,
    ConnectionPool,
    connect,
)
