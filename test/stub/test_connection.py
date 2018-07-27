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


from neobolt.bolt.connection import Connection, connect, RUN, PULL_ALL
from neobolt.bolt.response import Response
from neobolt.exceptions import ServiceUnavailable

from test.stub.tools import StubTestCase, StubCluster


class RunResponse(Response):

    pass


class PullAllResponse(Response):

    def __init__(self, connection):
        super(PullAllResponse, self).__init__(connection)
        self.records = []

    def on_records(self, records):
        self.records.extend(records)


class ConnectionTestCase(StubTestCase):

    def test_construction(self):
        with StubCluster({9001: "empty.script"}):
            address = ("127.0.0.1", 9001)
            with connect(address, auth=self.auth_token, encrypted=False) as cx:
                self.assertIsInstance(cx, Connection)

    def test_return_1(self):
        with StubCluster({9001: "return_1.script"}):
            address = ("127.0.0.1", 9001)
            with connect(address, auth=self.auth_token, encrypted=False) as cx:
                run_response = RunResponse(cx)
                pull_all_response = PullAllResponse(cx)
                cx.append(RUN, ("RETURN $x", {"x": 1}), response=run_response)
                cx.append(PULL_ALL, response=pull_all_response)
                cx.sync()
                self.assertEqual([[1]], pull_all_response.records)

    def test_disconnect_on_run(self):
        with StubCluster({9001: "disconnect_on_run.script"}):
            address = ("127.0.0.1", 9001)
            with connect(address, auth=self.auth_token, encrypted=False) as cx:
                with self.assertRaises(ServiceUnavailable):
                    run_response = RunResponse(cx)
                    cx.append(RUN, ("RETURN $x", {"x": 1}), response=run_response)
                    cx.sync()

    def test_disconnect_on_pull_all(self):
        with StubCluster({9001: "disconnect_on_pull_all.script"}):
            address = ("127.0.0.1", 9001)
            with connect(address, auth=self.auth_token, encrypted=False) as cx:
                with self.assertRaises(ServiceUnavailable):
                    run_response = RunResponse(cx)
                    pull_all_response = PullAllResponse(cx)
                    cx.append(RUN, ("RETURN $x", {"x": 1}), response=run_response)
                    cx.append(PULL_ALL, response=pull_all_response)
                    cx.sync()

    def test_disconnect_after_init(self):
        with StubCluster({9001: "disconnect_after_init.script"}):
            address = ("127.0.0.1", 9001)
            with connect(address, auth=self.auth_token, encrypted=False) as cx:
                with self.assertRaises(ServiceUnavailable):
                    cx.append(RUN, ("RETURN $x", {"x": 1}), response=RunResponse(cx))
                    cx.sync()
