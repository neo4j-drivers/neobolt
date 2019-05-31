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

from pytest import raises

from neobolt.direct import DEFAULT_PORT, Connection, connect
from neobolt.exceptions import ServiceUnavailable, TransientError, AuthError


def fail(metadata):
    raise RuntimeError(metadata)


def test_insecure_by_default(connection):
    assert not connection.secure


def test_can_be_secured(secure_connection):
    assert secure_connection.secure


def test_connection_type(connection):
    assert isinstance(connection, Connection)


def test_connection_simple_run(connection):
    records = []
    metadata = {}
    connection.run("RETURN 1", {}, on_success=metadata.update)
    connection.pull_all(on_records=records.extend, on_success=metadata.update)
    connection.send_all()
    connection.fetch_all()
    assert records == [[1]]


def test_custom_resolver(neo4j):
    address = ("*", DEFAULT_PORT)
    bolt_port = neo4j.addresses[0][1]

    def my_resolver(unresolved_address):
        assert unresolved_address == ("*", DEFAULT_PORT)
        yield "99.99.99.99", bolt_port   # should be rejected as can't connect
        yield "127.0.0.1", bolt_port     # should succeed

    with connect(address, auth=neo4j.auth, resolver=my_resolver) as cx:
        assert cx.server.address == ("127.0.0.1", 7687)


def test_multiple_chunk_response(connection):
    b = bytearray(16365)
    records = []
    metadata = {}
    connection.run("CREATE (a) SET a.foo = $x RETURN a", {"x": b},
                   on_success=metadata.update)
    connection.pull_all(on_records=records.extend, on_success=metadata.update)
    connection.send_all()
    connection.fetch_all()
    foo = records[0][0][2]["foo"]
    assert b == foo


def test_return_1(connection):
    metadata = {}
    records = []
    connection.run("RETURN $x", {"x": 1}, on_success=metadata.update)
    connection.pull_all(on_success=metadata.update, on_records=records.extend)
    connection.send_all()
    connection.fetch_all()
    assert records == [[1]]


def test_return_1_in_tx(connection):
    metadata = {}
    records = []
    connection.begin(on_success=metadata.update)
    connection.run("RETURN $x", {"x": 1}, on_success=metadata.update)
    connection.pull_all(on_success=metadata.update, on_records=records.extend)
    connection.commit(on_success=metadata.update)
    connection.send_all()
    connection.fetch_all()
    assert records == [[1]]
    assert metadata["bookmark"].startswith("neo4j:bookmark:")
    assert metadata["fields"] == ["$x"]
    assert isinstance(metadata["t_first"], int)
    assert isinstance(metadata["t_last"], int)
    assert metadata["type"] == "r"


def test_begin_with_metadata(connection):
    metadata = {}
    records = []
    connection.begin(metadata={"foo": "bar"})
    connection.run("CALL dbms.getTXMetaData", on_success=metadata.update)
    connection.pull_all(on_success=metadata.update, on_records=records.extend)
    connection.commit()
    connection.send_all()
    connection.fetch_all()
    assert records == [[{"foo": "bar"}]]


def test_begin_with_timeout(neo4j, delete_all_afterwards):
    with connect(neo4j.addresses[0], auth=neo4j.auth) as cx1:
        cx1.run("CREATE (a:Node)")
        cx1.discard_all()
        cx1.send_all()
        cx1.fetch_all()
        with connect(neo4j.addresses[0], auth=neo4j.auth) as cx2:
            cx1.begin()
            cx1.run("MATCH (a:Node) SET a.property = 1")
            cx1.send_all()
            cx1.fetch_all()
            cx2.begin(timeout=0.25)
            cx2.run("MATCH (a:Node) SET a.property = 2")
            with raises(TransientError):
                cx2.send_all()
                cx2.fetch_all()


def test_run_with_metadata(connection):
    metadata = {}
    records = []
    connection.run("CALL dbms.getTXMetaData", metadata={"foo": "bar"},
                   on_success=metadata.update)
    connection.pull_all(on_success=metadata.update, on_records=records.extend)
    connection.send_all()
    connection.fetch_all()
    assert records == [[{"foo": "bar"}]]


def test_run_with_timeout(neo4j, delete_all_afterwards):
    with connect(neo4j.addresses[0], auth=neo4j.auth) as cx1:
        cx1.run("CREATE (a:Node)")
        cx1.discard_all()
        cx1.send_all()
        cx1.fetch_all()
        with connect(neo4j.addresses[0], auth=neo4j.auth) as cx2:
            cx1.begin()
            cx1.run("MATCH (a:Node) SET a.property = 1")
            cx1.send_all()
            cx1.fetch_all()
            cx2.run("MATCH (a:Node) SET a.property = 2", timeout=0.25)
            with raises(TransientError):
                cx2.send_all()
                cx2.fetch_all()


def test_empty_auth(neo4j):
    with raises(AuthError):
        _ = connect(neo4j.addresses[0], auth=())


def test_empty_password(neo4j):
    with raises(AuthError):
        _ = connect(neo4j.addresses[0], auth=(neo4j.auth[0],))


def test_null_password(neo4j):
    with raises(AuthError):
        _ = connect(neo4j.addresses[0], auth=(neo4j.auth[0], None))


def test_null_user_and_password(neo4j):
    with raises(AuthError):
        _ = connect(neo4j.addresses[0], auth=(None, None))


def test_non_string_password(neo4j, neo4j_version):
    if (3, 5, 0) <= neo4j_version <= (3, 5, 3):
        raise SkipTest("Non-string passwords are broken in server "
                       "version %r" % neo4j_version)
    with raises(AuthError):
        _ = connect(neo4j.addresses[0], auth=(neo4j.auth[0], 1))


def test_non_string_user_and_password(neo4j, neo4j_version):
    if (3, 5, 0) <= neo4j_version <= (3, 5, 3):
        raise SkipTest("Non-string passwords are broken in server "
                       "version %r" % neo4j_version)
    with raises(AuthError):
        _ = connect(neo4j.addresses[0], auth=(1, 1))
