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


from unittest import SkipTest

from neobolt.direct import DEFAULT_PORT, Connection, connect
from neobolt.exceptions import ServiceUnavailable, TransientError, AuthError

from test.integration.tools import IntegrationTestCase


def fail(metadata):
    raise RuntimeError(metadata)


class ConnectionTestCase(IntegrationTestCase):

    def test_insecure_by_default(self):
        with connect(self.bolt_address, auth=self.auth_token) as cx:
            self.assertFalse(cx.secure)

    def test_can_be_secured(self):
        with connect(self.bolt_address, auth=self.auth_token, encrypted=True) as cx:
            self.assertTrue(cx.secure)

    def test_connection_open_close(self):
        with connect(self.bolt_address, auth=self.auth_token) as cx:
            self.assertIsInstance(cx, Connection)

    def test_connection_simple_run(self):
        records = []
        with connect(self.bolt_address, auth=self.auth_token) as cx:
            metadata = {}
            cx.run("RETURN 1", {}, on_success=metadata.update)
            cx.pull_all(on_records=records.extend, on_success=metadata.update)
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

    def test_multiple_chunk_response(self):
        b = bytearray(16365)
        records = []
        with connect(self.bolt_address, auth=self.auth_token) as cx:
            metadata = {}
            cx.run("CREATE (a) SET a.foo = $x RETURN a", {"x": b}, on_success=metadata.update)
            cx.pull_all(on_records=records.extend, on_success=metadata.update)
            cx.sync()
        foo = records[0][0][2]["foo"]
        self.assertEqual(b, foo)


class ConnectionV3IntegrationTestCase(IntegrationTestCase):

    def setUp(self):
        if self.protocol_version() < 3:
            raise SkipTest("Test requires Bolt v3")

    def test_return_1(self):
        with connect(self.bolt_address, auth=self.auth_token) as cx:
            metadata = {}
            records = []
            cx.run("RETURN $x", {"x": 1}, on_success=metadata.update)
            cx.pull_all(on_success=metadata.update, on_records=records.extend)
            cx.sync()
            self.assertEqual([[1]], records)

    def test_return_1_in_tx(self):
        with connect(self.bolt_address, auth=self.auth_token) as cx:
            metadata = {}
            records = []
            cx.begin(on_success=metadata.update)
            cx.run("RETURN $x", {"x": 1}, on_success=metadata.update)
            cx.pull_all(on_success=metadata.update, on_records=records.extend)
            cx.commit(on_success=metadata.update)
            cx.sync()
            self.assertEqual([[1]], records)
            self.assertTrue(metadata["bookmark"].startswith("neo4j:bookmark:"))
            self.assertEqual(metadata["fields"], ["$x"])
            self.assertIsInstance(metadata["t_first"], int)
            self.assertIsInstance(metadata["t_last"], int)
            self.assertEqual(metadata["type"], "r")

    def test_begin_with_metadata(self):
        with connect(self.bolt_address, auth=self.auth_token) as cx:
            metadata = {}
            records = []
            cx.begin(metadata={"foo": "bar"})
            cx.run("CALL dbms.getTXMetaData", on_success=metadata.update)
            cx.pull_all(on_success=metadata.update, on_records=records.extend)
            cx.commit()
            cx.sync()
            self.assertEqual([[{"foo": "bar"}]], records)

    def test_begin_with_timeout(self):
        try:
            with connect(self.bolt_address, auth=self.auth_token) as cx1:
                cx1.run("CREATE (a:Node)")
                cx1.discard_all()
                cx1.sync()
                with connect(self.bolt_address, auth=self.auth_token) as cx2:
                    cx1.begin()
                    cx1.run("MATCH (a:Node) SET a.property = 1")
                    cx1.sync()
                    cx2.begin(timeout=0.25)
                    cx2.run("MATCH (a:Node) SET a.property = 2")
                    with self.assertRaises(TransientError):
                        cx2.sync()
        finally:
            self.delete_all()

    def test_run_with_metadata(self):
        with connect(self.bolt_address, auth=self.auth_token) as cx:
            metadata = {}
            records = []
            cx.run("CALL dbms.getTXMetaData", metadata={"foo": "bar"}, on_success=metadata.update)
            cx.pull_all(on_success=metadata.update, on_records=records.extend)
            cx.sync()
            self.assertEqual([[{"foo": "bar"}]], records)

    def test_run_with_timeout(self):
        try:
            with connect(self.bolt_address, auth=self.auth_token) as cx1:
                cx1.run("CREATE (a:Node)")
                cx1.discard_all()
                cx1.sync()
                with connect(self.bolt_address, auth=self.auth_token) as cx2:
                    cx1.begin()
                    cx1.run("MATCH (a:Node) SET a.property = 1")
                    cx1.sync()
                    cx2.run("MATCH (a:Node) SET a.property = 2", timeout=0.25)
                    with self.assertRaises(TransientError):
                        cx2.sync()
        finally:
            self.delete_all()


class AuthTestCase(IntegrationTestCase):

    def test_empty_auth(self):
        with self.assertRaises(AuthError):
            _ = connect(self.bolt_address, auth=())

    def test_empty_password(self):
        with self.assertRaises(AuthError):
            _ = connect(self.bolt_address, auth=(self.user,))

    def test_null_password(self):
        with self.assertRaises(AuthError):
            _ = connect(self.bolt_address, auth=(self.user, None))

    def test_null_user_and_password(self):
        with self.assertRaises(AuthError):
            _ = connect(self.bolt_address, auth=(None, None))

    def test_non_string_password(self):
        with self.assertRaises(AuthError):
            _ = connect(self.bolt_address, auth=(self.user, 1))

    def test_non_string_user_and_password(self):
        with self.assertRaises(AuthError):
            _ = connect(self.bolt_address, auth=(1, 1))
