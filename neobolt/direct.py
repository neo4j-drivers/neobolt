#!/usr/bin/env python
# -*- encoding: utf-8 -*-

# Copyright (c) 2002-2018 "Neo4j,"
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


from neobolt.bolt.connection import ConnectionPool, ConnectionErrorHandler


class DirectConnectionErrorHandler(ConnectionErrorHandler):
    """ Handler for errors in direct driver connections.
    """

    def __init__(self):
        super(DirectConnectionErrorHandler, self).__init__({})  # does not need to handle errors


class DirectConnectionPool(ConnectionPool):

    def __init__(self, connector, address, **config):
        super(DirectConnectionPool, self).__init__(connector, DirectConnectionErrorHandler(), **config)
        self.address = address

    def acquire(self, access_mode=None):
        return self.acquire_direct(self.address)
