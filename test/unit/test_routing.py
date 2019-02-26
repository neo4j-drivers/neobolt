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


from unittest import TestCase

from neobolt.direct import connect
from neobolt.routing import RoutingConnectionPool


def connector(address):
    return connect(address, auth=("neotest", "neotest"))


class RoutingConnectionPoolConstructionTestCase(TestCase):

    def test_should_populate_initial_router(self):
        initial_router = ("127.0.0.1", 9001)
        router = ("127.0.0.1", 9002)
        with RoutingConnectionPool(connector, initial_router, {}, router) as pool:
            assert pool.routing_table.routers == {("127.0.0.1", 9002)}
