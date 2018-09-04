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


from neobolt.direct import connect, Connection
from neobolt.exceptions import ServiceUnavailable

from test.stub.tools import StubTestCase, StubCluster


class ConnectionV1TestCase(StubTestCase):

    def test_construction(self):
        with StubCluster({9001: "v1/empty.script"}):
            address = ("127.0.0.1", 9001)
            with connect(address, auth=self.auth_token, encrypted=False) as cx:
                self.assertIsInstance(cx, Connection)

    def test_return_1(self):
        with StubCluster({9001: "v1/return_1.script"}):
            address = ("127.0.0.1", 9001)
            with connect(address, auth=self.auth_token, encrypted=False) as cx:
                metadata = {}
                records = []
                cx.run("RETURN $x", {"x": 1}, on_success=metadata.update)
                cx.pull_all(on_success=metadata.update, on_records=records.extend)
                cx.sync()
                self.assertEqual([[1]], records)

    def test_disconnect_on_run(self):
        with StubCluster({9001: "v1/disconnect_on_run.script"}):
            address = ("127.0.0.1", 9001)
            with connect(address, auth=self.auth_token, encrypted=False) as cx:
                with self.assertRaises(ServiceUnavailable):
                    metadata = {}
                    cx.run("RETURN $x", {"x": 1}, on_success=metadata.update)
                    cx.sync()

    def test_disconnect_on_pull_all(self):
        with StubCluster({9001: "v1/disconnect_on_pull_all.script"}):
            address = ("127.0.0.1", 9001)
            with connect(address, auth=self.auth_token, encrypted=False) as cx:
                with self.assertRaises(ServiceUnavailable):
                    metadata = {}
                    records = []
                    cx.run("RETURN $x", {"x": 1}, on_success=metadata.update)
                    cx.pull_all(on_success=metadata.update, on_records=records.extend)
                    cx.sync()

    def test_disconnect_after_init(self):
        with StubCluster({9001: "v1/disconnect_after_init.script"}):
            address = ("127.0.0.1", 9001)
            with connect(address, auth=self.auth_token, encrypted=False) as cx:
                with self.assertRaises(ServiceUnavailable):
                    metadata = {}
                    cx.run("RETURN $x", {"x": 1}, on_success=metadata.update)
                    cx.sync()


class ConnectionV3TestCase(StubTestCase):

    def test_construction(self):
        with StubCluster({9001: "v3/empty.script"}):
            address = ("127.0.0.1", 9001)
            with connect(address, auth=self.auth_token, encrypted=False) as cx:
                self.assertIsInstance(cx, Connection)

    def test_return_1(self):
        with StubCluster({9001: "v3/return_1.script"}):
            address = ("127.0.0.1", 9001)
            with connect(address, auth=self.auth_token, encrypted=False) as cx:
                metadata = {}
                records = []
                cx.run("RETURN $x", {"x": 1}, on_success=metadata.update)
                cx.pull_all(on_success=metadata.update, on_records=records.extend)
                cx.sync()
                self.assertEqual([[1]], records)

    def test_return_1_in_tx(self):
        with StubCluster({9001: "v3/return_1_in_tx.script"}):
            address = ("127.0.0.1", 9001)
            with connect(address, auth=self.auth_token, encrypted=False) as cx:
                metadata = {}
                records = []
                cx.begin(on_success=metadata.update)
                cx.run("RETURN $x", {"x": 1}, on_success=metadata.update)
                cx.pull_all(on_success=metadata.update, on_records=records.extend)
                cx.commit(on_success=metadata.update)
                cx.sync()
                self.assertEqual([[1]], records)
                self.assertEqual({"fields": ["x"], "bookmark": "bookmark:1"}, metadata)

    def test_begin_with_metadata(self):
        with StubCluster({9001: "v3/begin_with_metadata.script"}):
            address = ("127.0.0.1", 9001)
            with connect(address, auth=self.auth_token, encrypted=False) as cx:
                metadata = {}
                records = []
                cx.begin(metadata={"mode": "r"}, on_success=metadata.update)
                cx.run("RETURN $x", {"x": 1}, on_success=metadata.update)
                cx.pull_all(on_success=metadata.update, on_records=records.extend)
                cx.commit(on_success=metadata.update)
                cx.sync()
                self.assertEqual([[1]], records)
                self.assertEqual({"fields": ["x"], "bookmark": "bookmark:1"}, metadata)

    def test_begin_with_timeout(self):
        with StubCluster({9001: "v3/begin_with_timeout.script"}):
            address = ("127.0.0.1", 9001)
            with connect(address, auth=self.auth_token, encrypted=False) as cx:
                metadata = {}
                records = []
                cx.begin(timeout=12.34, on_success=metadata.update)
                cx.run("RETURN $x", {"x": 1}, on_success=metadata.update)
                cx.pull_all(on_success=metadata.update, on_records=records.extend)
                cx.commit(on_success=metadata.update)
                cx.sync()
                self.assertEqual([[1]], records)
                self.assertEqual({"fields": ["x"], "bookmark": "bookmark:1"}, metadata)

    def test_run_with_metadata(self):
        with StubCluster({9001: "v3/run_with_metadata.script"}):
            address = ("127.0.0.1", 9001)
            with connect(address, auth=self.auth_token, encrypted=False) as cx:
                metadata = {}
                records = []
                cx.run("RETURN $x", {"x": 1}, metadata={"mode": "r"}, on_success=metadata.update)
                cx.pull_all(on_success=metadata.update, on_records=records.extend)
                cx.sync()
                self.assertEqual([[1]], records)

    def test_run_with_timeout(self):
        with StubCluster({9001: "v3/run_with_timeout.script"}):
            address = ("127.0.0.1", 9001)
            with connect(address, auth=self.auth_token, encrypted=False) as cx:
                metadata = {}
                records = []
                cx.run("RETURN $x", {"x": 1}, timeout=12.34, on_success=metadata.update)
                cx.pull_all(on_success=metadata.update, on_records=records.extend)
                cx.sync()
                self.assertEqual([[1]], records)

    def test_disconnect_on_run(self):
        with StubCluster({9001: "v3/disconnect_on_run.script"}):
            address = ("127.0.0.1", 9001)
            with connect(address, auth=self.auth_token, encrypted=False) as cx:
                with self.assertRaises(ServiceUnavailable):
                    metadata = {}
                    cx.run("RETURN $x", {"x": 1}, on_success=metadata.update)
                    cx.sync()

    def test_disconnect_on_pull_all(self):
        with StubCluster({9001: "v3/disconnect_on_pull_all.script"}):
            address = ("127.0.0.1", 9001)
            with connect(address, auth=self.auth_token, encrypted=False) as cx:
                with self.assertRaises(ServiceUnavailable):
                    metadata = {}
                    records = []
                    cx.run("RETURN $x", {"x": 1}, on_success=metadata.update)
                    cx.pull_all(on_success=metadata.update, on_records=records.extend)
                    cx.sync()

    def test_disconnect_after_init(self):
        with StubCluster({9001: "v3/disconnect_after_init.script"}):
            address = ("127.0.0.1", 9001)
            with connect(address, auth=self.auth_token, encrypted=False) as cx:
                with self.assertRaises(ServiceUnavailable):
                    metadata = {}
                    cx.run("RETURN $x", {"x": 1}, on_success=metadata.update)
                    cx.sync()
