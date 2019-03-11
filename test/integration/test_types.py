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


from datetime import date
from math import isnan
from unittest import SkipTest

from pytz import FixedOffset, timezone, utc

from neobolt.direct import connect
from neobolt.exceptions import CypherTypeError
from neobolt.types import Structure
from neobolt.types.graph import Node, Relationship, Path, hydrate_path
from neobolt.types.spatial import CartesianPoint, WGS84Point, hydrate_point, dehydrate_point
from neobolt.types.temporal import Duration, Date, Time, DateTime, dehydrate_date

from .tools import IntegrationTestCase


# def run_and_rollback(tx, statement, **parameters):
#     result = tx.run(statement, **parameters)
#     value = result.single().value()
#     tx.success = False
#     return value


class TypeSystemIntegrationTestCase(IntegrationTestCase):

    def _test(self, statement, parameters, assertion):
        data = []
        metadata = {}
        with connect(self.bolt_address, auth=self.auth_token) as cx:
            cx.begin()
            cx.run(statement, parameters, on_success=metadata.update)
            cx.pull_all(on_records=data.extend, on_success=metadata.update)
            cx.rollback()
            cx.sync()
        assertion(data, metadata)

    def _test_io(self, *values):
        value_list = list(values)
        self._test("RETURN $x", {"x": value_list}, lambda d, m: self.assertEqual(d, [[value_list]]))


class CoreTypeOutputTestCase(TypeSystemIntegrationTestCase):

    def test_null(self):
        self._test_io(None)

    def test_boolean(self):
        self._test_io(True, False)

    def test_integer(self):
        for e in range(63):
            n0 = 2 ** e
            for n in [n0, -n0]:
                self._test_io(n - 1, n, n + 1)

    def test_float(self):
        self._test_io(0.0, 3.1415926, float("+Inf"), float("-Inf"))

    def test_float_nan(self):
        not_a_number = float("NaN")
        self._test("RETURN $x", {"x": not_a_number}, lambda d, m: self.assertTrue(isnan(d[0][0])))

    def test_string(self):
        self._test("RETURN 'hello, world'", {}, lambda d, m: self.assertEqual(d, [["hello, world"]]))

    def test_bytes(self):
        self._test_io(bytearray([0x00, 0x33, 0x66, 0x99, 0xCC, 0xFF]))

    def test_list(self):
        self._test_io(["one", "two", "three"])

    def test_dictionary(self):
        self._test_io({"one": "eins", "two": "zwei", "three": "drei"})

    # TODO: trap this in connector to avoid closed connections
    # def test_non_string_dictionary_keys(self):
    #     with self.assertRaises(TypeError):
    #         self._test_io({1: "eins", 2: "zwei", 3: "drei"})


class GraphTypeOutputTestCase(TypeSystemIntegrationTestCase):

    def test_node(self):
        self._test("CREATE (a:Person {name:'Alice'}) RETURN a", {},
                   lambda d, m: self.assertEqual(d, [[
                       Structure(b"N", d[0][0][0], ["Person"], {"name": "Alice"}),
                   ]]))

    def test_relationship(self):
        self._test("CREATE (a)-[r:KNOWS {since:1999}]->(b) RETURN r, id(a), id(b)", {},
                   lambda d, m: self.assertEqual(d, [[
                       Structure(b"R", d[0][0][0], d[0][1], d[0][2], "KNOWS", {"since": 1999}),
                       d[0][1],
                       d[0][2],
                   ]]))

    def test_path(self):

        def assertion(data, _):
            p, a, b, c, ab, bc = data[0]
            self.assertIsInstance(p, Structure)
            self.assertEqual(p.tag, b"P")
            self.assertIsInstance(p[0], list)
            self.assertIsInstance(p[1], list)
            self.assertIsInstance(p[2], list)

        self._test("CREATE p=(a)-[ab:X]->(b)-[bc:X]->(c) RETURN p, a, b, c, ab, bc", {}, assertion)


class SpatialTypeInputTestCase(TypeSystemIntegrationTestCase):

    def test_cartesian_point(self):
        self.assert_supports_spatial_types()

        def assertion(data, _):
            x, y = data[0]
            self.assertEqual(x, 1.23)
            self.assertEqual(y, 4.56)

        point = dehydrate_point(CartesianPoint((1.23, 4.56)))
        self._test("CYPHER runtime=interpreted WITH $point AS point "
                   "RETURN point.x, point.y",
                   {"point": point}, assertion)

    def test_cartesian_3d_point(self):
        self.assert_supports_spatial_types()

        def assertion(data, _):
            x, y, z = data[0]
            self.assertEqual(x, 1.23)
            self.assertEqual(y, 4.56)
            self.assertEqual(z, 7.89)

        point = dehydrate_point(CartesianPoint((1.23, 4.56, 7.89)))
        self._test("CYPHER runtime=interpreted WITH $point AS point "
                   "RETURN point.x, point.y, point.z",
                   {"point": point}, assertion)

    def test_wgs84_point(self):
        self.assert_supports_spatial_types()

        def assertion(data, _):
            latitude, longitude = data[0]
            self.assertEqual(longitude, 1.23)
            self.assertEqual(latitude, 4.56)

        point = dehydrate_point(WGS84Point((1.23, 4.56)))
        self._test("CYPHER runtime=interpreted WITH $point AS point "
                   "RETURN point.latitude, point.longitude",
                   {"point": point}, assertion)

    def test_wgs84_3d_point(self):
        self.assert_supports_spatial_types()

        def assertion(data, _):
            latitude, longitude, height = data[0]
            self.assertEqual(longitude, 1.23)
            self.assertEqual(latitude, 4.56)
            self.assertEqual(height, 7.89)

        point = dehydrate_point(WGS84Point((1.23, 4.56, 7.89)))
        self._test("CYPHER runtime=interpreted WITH $point AS point "
                   "RETURN point.latitude, point.longitude, point.height",
                   {"point": point}, assertion)

    def test_point_array(self):
        self.assert_supports_spatial_types()

        points = [dehydrate_point(WGS84Point((1.23, 4.56))),
                  dehydrate_point(WGS84Point((9.87, 6.54)))]

        def assertion(data, _):
            self.assertEqual(points, data[0][0])

        self._test("CREATE (a {x:$x}) RETURN a.x",
                   {"x": points}, assertion)


class SpatialTypeOutputTestCase(TypeSystemIntegrationTestCase):

    def test_cartesian_point(self):
        self.assert_supports_spatial_types()

        def assertion(data, _):
            value = hydrate_point(*data[0][0])
            self.assertIsInstance(value, CartesianPoint)
            self.assertEqual(value.x, 3.0)
            self.assertEqual(value.y, 4.0)
            with self.assertRaises(AttributeError):
                _ = value.z

        self._test("RETURN point({x:3, y:4})", {}, assertion)

    def test_cartesian_3d_point(self):
        self.assert_supports_spatial_types()

        def assertion(data, _):
            value = hydrate_point(*data[0][0])
            self.assertIsInstance(value, CartesianPoint)
            self.assertEqual(value.x, 3.0)
            self.assertEqual(value.y, 4.0)
            self.assertEqual(value.z, 5.0)

        self._test("RETURN point({x:3, y:4, z:5})", {}, assertion)

    def test_wgs84_point(self):
        self.assert_supports_spatial_types()

        def assertion(data, _):
            value = hydrate_point(*data[0][0])
            self.assertIsInstance(value, WGS84Point)
            self.assertEqual(value.latitude, 3.0)
            self.assertEqual(value.y, 3.0)
            self.assertEqual(value.longitude, 4.0)
            self.assertEqual(value.x, 4.0)
            with self.assertRaises(AttributeError):
                _ = value.height
            with self.assertRaises(AttributeError):
                _ = value.z

        self._test("RETURN point({latitude:3, longitude:4})", {}, assertion)

    def test_wgs84_3d_point(self):
        self.assert_supports_spatial_types()

        def assertion(data, _):
            value = hydrate_point(*data[0][0])
            self.assertIsInstance(value, WGS84Point)
            self.assertEqual(value.latitude, 3.0)
            self.assertEqual(value.y, 3.0)
            self.assertEqual(value.longitude, 4.0)
            self.assertEqual(value.x, 4.0)
            self.assertEqual(value.height, 5.0)
            self.assertEqual(value.z, 5.0)

        self._test("RETURN point({latitude:3, longitude:4, height:5})", {}, assertion)


class TemporalTypeInputTestCase(TypeSystemIntegrationTestCase):

    def test_native_date(self):
        self.assert_supports_temporal_types()

        def assertion(data, _):
            year, month, day = data[0]
            self.assertEqual(year, 1976)
            self.assertEqual(month, 6)
            self.assertEqual(day, 13)

        value = dehydrate_date(date(1976, 6, 13))
        self._test("CYPHER runtime=interpreted WITH $x AS x "
                   "RETURN x.year, x.month, x.day", {"x": value}, assertion)

    def test_date(self):
        self.assert_supports_temporal_types()

        def assertion(data, _):
            year, month, day = data[0]
            self.assertEqual(year, 1976)
            self.assertEqual(month, 6)
            self.assertEqual(day, 13)

        value = dehydrate_date(Date(1976, 6, 13))
        self._test("CYPHER runtime=interpreted WITH $x AS x "
                   "RETURN x.year, x.month, x.day", {"x": value}, assertion)
