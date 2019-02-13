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


from collections import OrderedDict
from unittest import TestCase

from neobolt.impl.python.routing import LeastConnectedLoadBalancingStrategy


class FakeConnectionPool(object):

    def __init__(self, addresses):
        self._addresses = addresses

    def in_use_connection_count(self, address):
        return self._addresses.get(address, 0)


class LeastConnectedLoadBalancingStrategyTestCase(TestCase):

    def test_simple_reader_selection(self):
        strategy = LeastConnectedLoadBalancingStrategy(FakeConnectionPool(OrderedDict([
            ("0.0.0.0", 2),
            ("1.1.1.1", 1),
            ("2.2.2.2", 0),
        ])))
        self.assertEqual(strategy.select_reader(["0.0.0.0", "1.1.1.1", "2.2.2.2"]), "2.2.2.2")

    def test_reader_selection_with_clash(self):
        strategy = LeastConnectedLoadBalancingStrategy(FakeConnectionPool(OrderedDict([
            ("0.0.0.0", 0),
            ("0.0.0.1", 0),
            ("1.1.1.1", 1),
        ])))
        self.assertEqual(strategy.select_reader(["0.0.0.0", "0.0.0.1", "1.1.1.1"]), "0.0.0.0")
        self.assertEqual(strategy.select_reader(["0.0.0.0", "0.0.0.1", "1.1.1.1"]), "0.0.0.1")

    def test_empty_reader_selection(self):
        strategy = LeastConnectedLoadBalancingStrategy(FakeConnectionPool(OrderedDict([
        ])))
        self.assertIsNone(strategy.select_reader([]))

    def test_not_in_pool_reader_selection(self):
        strategy = LeastConnectedLoadBalancingStrategy(FakeConnectionPool(OrderedDict([
            ("1.1.1.1", 1),
            ("2.2.2.2", 2),
        ])))
        self.assertEqual(strategy.select_reader(["2.2.2.2", "3.3.3.3"]), "3.3.3.3")

    def test_partially_in_pool_reader_selection(self):
        strategy = LeastConnectedLoadBalancingStrategy(FakeConnectionPool(OrderedDict([
            ("1.1.1.1", 1),
            ("2.2.2.2", 0),
        ])))
        self.assertEqual(strategy.select_reader(["2.2.2.2", "3.3.3.3"]), "2.2.2.2")
        self.assertEqual(strategy.select_reader(["2.2.2.2", "3.3.3.3"]), "3.3.3.3")

    def test_simple_writer_selection(self):
        strategy = LeastConnectedLoadBalancingStrategy(FakeConnectionPool(OrderedDict([
            ("0.0.0.0", 2),
            ("1.1.1.1", 1),
            ("2.2.2.2", 0),
        ])))
        self.assertEqual(strategy.select_writer(["0.0.0.0", "1.1.1.1", "2.2.2.2"]), "2.2.2.2")

    def test_writer_selection_with_clash(self):
        strategy = LeastConnectedLoadBalancingStrategy(FakeConnectionPool(OrderedDict([
            ("0.0.0.0", 0),
            ("0.0.0.1", 0),
            ("1.1.1.1", 1),
        ])))
        self.assertEqual(strategy.select_writer(["0.0.0.0", "0.0.0.1", "1.1.1.1"]), "0.0.0.0")
        self.assertEqual(strategy.select_writer(["0.0.0.0", "0.0.0.1", "1.1.1.1"]), "0.0.0.1")

    def test_empty_writer_selection(self):
        strategy = LeastConnectedLoadBalancingStrategy(FakeConnectionPool(OrderedDict([
        ])))
        self.assertIsNone(strategy.select_writer([]))

    def test_not_in_pool_writer_selection(self):
        strategy = LeastConnectedLoadBalancingStrategy(FakeConnectionPool(OrderedDict([
            ("1.1.1.1", 1),
            ("2.2.2.2", 2),
        ])))
        self.assertEqual(strategy.select_writer(["2.2.2.2", "3.3.3.3"]), "3.3.3.3")

    def test_partially_in_pool_writer_selection(self):
        strategy = LeastConnectedLoadBalancingStrategy(FakeConnectionPool(OrderedDict([
            ("1.1.1.1", 1),
            ("2.2.2.2", 0),
        ])))
        self.assertEqual(strategy.select_writer(["2.2.2.2", "3.3.3.3"]), "2.2.2.2")
        self.assertEqual(strategy.select_writer(["2.2.2.2", "3.3.3.3"]), "3.3.3.3")
