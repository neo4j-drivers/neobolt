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

from neobolt.impl.python.routing import OrderedSet


class OrderedSetTestCase(TestCase):

    def test_should_repr_as_set(self):
        s = OrderedSet([1, 2, 3])
        assert repr(s) == "{1, 2, 3}"

    def test_should_contain_element(self):
        s = OrderedSet([1, 2, 3])
        assert 2 in s

    def test_should_not_contain_non_element(self):
        s = OrderedSet([1, 2, 3])
        assert 4 not in s

    def test_should_be_able_to_get_item_if_empty(self):
        s = OrderedSet([])
        with self.assertRaises(IndexError):
            _ = s[0]

    def test_should_be_able_to_get_items_by_index(self):
        s = OrderedSet([1, 2, 3])
        self.assertEqual(s[0], 1)
        self.assertEqual(s[1], 2)
        self.assertEqual(s[2], 3)

    def test_should_be_iterable(self):
        s = OrderedSet([1, 2, 3])
        assert list(iter(s)) == [1, 2, 3]

    def test_should_have_length(self):
        s = OrderedSet([1, 2, 3])
        assert len(s) == 3

    def test_should_be_able_to_add_new(self):
        s = OrderedSet([1, 2, 3])
        s.add(4)
        assert list(s) == [1, 2, 3, 4]

    def test_should_be_able_to_add_existing(self):
        s = OrderedSet([1, 2, 3])
        s.add(2)
        assert list(s) == [1, 2, 3]

    def test_should_be_able_to_clear(self):
        s = OrderedSet([1, 2, 3])
        s.clear()
        assert list(s) == []

    def test_should_be_able_to_discard_existing(self):
        s = OrderedSet([1, 2, 3])
        s.discard(2)
        assert list(s) == [1, 3]

    def test_should_be_able_to_discard_non_existing(self):
        s = OrderedSet([1, 2, 3])
        s.discard(4)
        assert list(s) == [1, 2, 3]

    def test_should_be_able_to_remove_existing(self):
        s = OrderedSet([1, 2, 3])
        s.remove(2)
        assert list(s) == [1, 3]

    def test_should_not_be_able_to_remove_non_existing(self):
        s = OrderedSet([1, 2, 3])
        with self.assertRaises(ValueError):
            s.remove(4)

    def test_should_be_able_to_update(self):
        s = OrderedSet([1, 2, 3])
        s.update([3, 4, 5])
        assert list(s) == [1, 2, 3, 4, 5]

    def test_should_be_able_to_replace(self):
        s = OrderedSet([1, 2, 3])
        s.replace([3, 4, 5])
        assert list(s) == [3, 4, 5]
