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


from os import getenv, makedirs
from os.path import basename, dirname, join as path_join, isfile
from shutil import copyfile
from sys import stderr
from unittest import TestCase
from urllib.request import urlretrieve

from boltkit.server import Neo4jService

from neobolt.direct import connect

from test.env import NEO4J_SERVER_PACKAGE, NEO4J_USER, NEO4J_PASSWORD, \
    NEOCTRL_ARGS


def copy_dist(source, target):
    if isfile(target) and "SNAPSHOT" not in basename(source):
        return target
    try:
        makedirs(dirname(target))
    except OSError:
        pass
    if source.startswith("http:"):
        stderr.write("Downloading package from {}\n".format(source))
        urlretrieve(source, target)
        return target
    else:
        return copyfile(source, target)


def is_listening(address):
    from socket import create_connection
    try:
        s = create_connection(address)
    except IOError:
        return False
    else:
        s.close()
        return True


class ServerVersion(object):
    def __init__(self, product, version_tuple, tags_tuple):
        self.product = product
        self.version_tuple = version_tuple
        self.tags_tuple = tags_tuple

    def at_least_version(self, major, minor):
        return self.version_tuple >= (major, minor)

    @classmethod
    def from_str(cls, full_version):
        if full_version is None:
            return ServerVersion("Neo4j", (3, 0), ())
        product, _, tagged_version = full_version.partition("/")
        tags = tagged_version.split("-")
        version = map(int, tags[0].split("."))
        return ServerVersion(product, tuple(version), tuple(tags[1:]))


class IntegrationTestCase(TestCase):
    """ Base class for test cases that integrate with a server.
    """

    bolt_port = 7687
    bolt_address = ("localhost", bolt_port)

    bolt_uri = "bolt://%s:%d" % bolt_address
    bolt_routing_uri = "bolt+routing://%s:%d" % bolt_address

    user = NEO4J_USER or "neo4j"
    password = NEO4J_PASSWORD or "password"
    auth_token = (user, password)

    controller = None
    dist_path = path_join(dirname(__file__), "dist")
    run_path = path_join(dirname(__file__), "run")

    server_package = NEO4J_SERVER_PACKAGE
    local_server_package = path_join(dist_path, basename(server_package)) if server_package else None
    neoctrl_args = NEOCTRL_ARGS

    neo4j = None

    @classmethod
    def delete_all(cls):
        with connect(cls.bolt_address, auth=cls.auth_token) as cx:
            cx.run("MATCH (a) DETACH DELETE a")
            cx.discard_all()
            cx.send_all()
            cx.fetch_all()

    @classmethod
    def server_version_info(cls):
        with connect(cls.bolt_address, auth=cls.auth_token) as cx:
            full_version = cx.server.agent
            return ServerVersion.from_str(full_version)

    @classmethod
    def at_least_server_version(cls, major, minor):
        return cls.server_version_info().at_least_version(major, minor)

    @classmethod
    def protocol_version(cls):
        with connect(cls.bolt_address, auth=cls.auth_token) as cx:
            return cx.protocol_version

    @classmethod
    def at_least_protocol_version(cls, version):
        return cls.protocol_version() >= version

    @classmethod
    def setUpClass(cls):
        docker_tag = getenv("NEO4J_VERSION")
        if docker_tag is None:
            docker_tag = "enterprise"
        else:
            docker_tag += "-enterprise"
        print("Running contained Neo4j using Docker tag {}".format(docker_tag))
        cls.neo4j = Neo4jService(
            image=docker_tag,
            auth=cls.auth_token, **{
                "dbms.connectors.default_listen_address": "::",
            }
        )
        cls.neo4j.start(timeout=30)

    @classmethod
    def tearDownClass(cls):
        cls.neo4j.stop()
