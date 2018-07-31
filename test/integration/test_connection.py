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


from neobolt.bolt import DEFAULT_PORT, Connection, connect, ServiceUnavailable, Response

from test.integration.tools import IntegrationTestCase


def fail(metadata):
    raise RuntimeError(metadata)


class ConnectionTestCase(IntegrationTestCase):

    def test_connection_open_close(self):
        with connect(self.bolt_address, auth=self.auth_token) as cx:
            self.assertIsInstance(cx, Connection)

    def test_connection_simple_run(self):
        records = []
        with connect(self.bolt_address, auth=self.auth_token) as cx:
            metadata = {}
            cx.run("RETURN 1", {}, metadata)
            cx.pull_all(metadata, records)
            cx.sync()
        self.assertEqual(records, [[1]])

    def test_fail_nicely_when_using_http_port(self):
        with self.assertRaises(ServiceUnavailable) as cm:
            connect(("localhost", 7474), auth=self.auth_token)
        self.assertIn("HTTP", cm.exception.args[0])

    def test_custom_resolver(self):
        address = ("*", DEFAULT_PORT)

        def my_resolver(unresolved_address):
            self.assertEqual(unresolved_address, ("*", DEFAULT_PORT))
            yield "99.99.99.99", self.bolt_port     # this should be rejected as unable to connect
            yield "127.0.0.1", self.bolt_port       # this should succeed

        with connect(address, auth=self.auth_token, resolver=my_resolver) as cx:
            self.assertEqual(cx.server.address, ("127.0.0.1", 7687))
