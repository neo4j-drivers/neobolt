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


from __future__ import unicode_literals

from unittest import TestCase

from neobolt.versioning import Version


class VersionTestCase(TestCase):

    def test_major_minor(self):
        v = Version.parse("1.2")
        self.assertEqual(v, ((1, 2),))

    def test_major_minor_patch(self):
        v = Version.parse("1.2.3")
        self.assertEqual(v, ((1, 2, 3),))

    def test_alpha(self):
        v = Version.parse("1.2.3-alpha01")
        self.assertEqual(v, ((1, 2, 3), ("alpha",), (1, )))

    def test_snapshot(self):
        v = Version.parse("1.2-snapshot")
        self.assertEqual(v, ((1, 2), ("snapshot",)))

    def test_double_dash(self):
        v = Version.parse("1.2--3")
        self.assertEqual(v, ((1, 2), (0,), (3,)))

    def test_double_dot(self):
        v = Version.parse("1.2..3")
        self.assertEqual(v, ((1, 2, 0, 3),))
