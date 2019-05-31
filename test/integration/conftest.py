#!/usr/bin/env python
# -*- encoding: utf-8 -*-

# Copyright 2011-2019, Nigel Small
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


from multiprocessing import current_process
from os import getenv

from boltkit.server import Neo4jService
from pytest import fixture

from neobolt.direct import connect


NEO4J_EDITION = "community"
NEO4J_VERSION = getenv("NEO4J_VERSION", "3.5")
NEO4J_PROTOCOLS = ["bolt", "http"]  # TODO: https/cert
NEO4J_HOST = "localhost"
NEO4J_PORTS = {
    "bolt": 7687,
    "http": 7474,
    "https": 7473,
}
NEO4J_USER = "neo4j"
NEO4J_PASSWORD = "password"
NEO4J_DEBUG = getenv("NEO4J_DEBUG", "")
NEO4J_PROCESS = {}


test_run_id = "{}.{}".format(current_process().pid, __name__)


@fixture(scope="session")
def neo4j():
    service = Neo4jService(test_run_id,
                           image="{}-enterprise".format(NEO4J_VERSION))
    service.start(timeout=30)
    return service


@fixture()
def connection(neo4j):
    with connect(neo4j.addresses[0], auth=neo4j.auth) as cx:
        yield cx


@fixture()
def secure_connection(neo4j):
    with connect(neo4j.addresses[0], auth=neo4j.auth, secure=True) as cx:
        yield cx


@fixture()
def neo4j_version(connection):
    return connection.server.version_info()


@fixture
def run_and_rollback(connection):

    def f(statement, parameters, assertion):
        data = []
        metadata = {}
        connection.begin()
        connection.run(statement, parameters, on_success=metadata.update)
        connection.pull_all(on_records=data.extend, on_success=metadata.update)
        connection.rollback()
        connection.send_all()
        connection.fetch_all()
        assertion(data, metadata)

    return f


@fixture()
def delete_all_afterwards(connection):
    yield
    connection.run("MATCH (a) DETACH DELETE a")
    connection.discard_all()
    connection.send_all()
    connection.fetch_all()


def pytest_sessionfinish(session, exitstatus):
    """ Called after the entire session to ensure Neo4j is shut down.
    """
    Neo4jService.find_and_stop(test_run_id)
