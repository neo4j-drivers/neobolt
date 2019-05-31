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

from pytest import fixture, raises

from neobolt.types import Structure
from neobolt.types.spatial import point_type, hydrate_point, dehydrate_point
from neobolt.types.temporal import Date, dehydrate_date


# Point subclass definitions
CartesianPoint = point_type("CartesianPoint", ["x", "y", "z"],
                            {2: 7203, 3: 9157})
WGS84Point = point_type("WGS84Point", ["longitude", "latitude", "height"],
                        {2: 4326, 3: 4979})


@fixture
def bounce(run_and_rollback):
    """ Runs an input-output test for one or more values.
    """

    def f(*values):
        value_list = list(values)

        def assertion(data, _):
            assert data == [[value_list]]

        run_and_rollback("RETURN $x", {"x": value_list}, assertion)

    return f


def test_null(bounce):
    bounce(None)


def test_boolean(bounce):
    bounce(True, False)


def test_integer(bounce):
    for e in range(63):
        n0 = 2 ** e
        for n in [n0, -n0]:
            bounce(n - 1, n, n + 1)


def test_float(bounce):
    bounce(0.0, 3.1415926, float("+Inf"), float("-Inf"))


def test_float_nan(run_and_rollback):
    not_a_number = float("NaN")

    def assertion(data, _):
        assert isnan(data[0][0])

    run_and_rollback("RETURN $x", {"x": not_a_number}, assertion)


def test_string(bounce):
    bounce("hello, world")


def test_bytes(bounce):
    bounce(bytearray([0x00, 0x33, 0x66, 0x99, 0xCC, 0xFF]))


def test_list(bounce):
    bounce(["one", "two", "three"])


def test_dictionary(bounce):
    bounce({"one": "eins", "two": "zwei", "three": "drei"})


def test_node(run_and_rollback):

    def assertion(data, _):
        assert data == [[
            Structure(b"N", data[0][0][0], ["Person"], {"name": "Alice"}),
        ]]

    run_and_rollback("CREATE (a:Person {name:'Alice'}) RETURN a", {}, assertion)


def test_relationship(run_and_rollback):

    def assertion(data, _):
        assert data == [[
            Structure(b"R", data[0][0][0], data[0][1], data[0][2], "KNOWS",
                      {"since": 1999}), data[0][1], data[0][2],
        ]]

    run_and_rollback("CREATE (a)-[r:KNOWS {since:1999}]->(b) "
                     "RETURN r, id(a), id(b)", {}, assertion)


def test_path(run_and_rollback):

    def assertion(data, _):
        p, a, b, c, ab, bc = data[0]
        assert isinstance(p, Structure)
        assert p.tag == b"P"
        assert isinstance(p[0], list)
        assert isinstance(p[1], list)
        assert isinstance(p[2], list)

    run_and_rollback("CREATE p=(a)-[ab:X]->(b)-[bc:X]->(c) "
                     "RETURN p, a, b, c, ab, bc", {}, assertion)


def test_cartesian_point_input(run_and_rollback):

    def assertion(data, _):
        x, y = data[0]
        assert x == 1.23
        assert y == 4.56

    point = dehydrate_point(CartesianPoint((1.23, 4.56)))
    run_and_rollback("CYPHER runtime=interpreted WITH $point AS point "
                     "RETURN point.x, point.y",
                     {"point": point}, assertion)


def test_cartesian_3d_point_input(run_and_rollback):

    def assertion(data, _):
        x, y, z = data[0]
        assert x == 1.23
        assert y == 4.56
        assert z == 7.89

    point = dehydrate_point(CartesianPoint((1.23, 4.56, 7.89)))
    run_and_rollback("CYPHER runtime=interpreted WITH $point AS point "
                     "RETURN point.x, point.y, point.z",
                     {"point": point}, assertion)


def test_wgs84_point_input(run_and_rollback):

    def assertion(data, _):
        latitude, longitude = data[0]
        assert longitude == 1.23
        assert latitude == 4.56

    point = dehydrate_point(WGS84Point((1.23, 4.56)))
    run_and_rollback("CYPHER runtime=interpreted WITH $point AS point "
                     "RETURN point.latitude, point.longitude",
                     {"point": point}, assertion)


def test_wgs84_3d_point_input(run_and_rollback):

    def assertion(data, _):
        latitude, longitude, height = data[0]
        assert longitude == 1.23
        assert latitude == 4.56
        assert height == 7.89

    point = dehydrate_point(WGS84Point((1.23, 4.56, 7.89)))
    run_and_rollback("CYPHER runtime=interpreted WITH $point AS point "
                     "RETURN point.latitude, point.longitude, point.height",
                     {"point": point}, assertion)


def test_point_array_input(run_and_rollback):

    points = [dehydrate_point(WGS84Point((1.23, 4.56))),
              dehydrate_point(WGS84Point((9.87, 6.54)))]

    def assertion(data, _):
        assert points == data[0][0]

    run_and_rollback("CREATE (a {x:$x}) RETURN a.x",
                     {"x": points}, assertion)


def test_cartesian_point_output(run_and_rollback):

    def assertion(data, _):
        value = hydrate_point(*data[0][0])
        assert isinstance(value, CartesianPoint)
        assert value.x == 3.0
        assert value.y == 4.0
        with raises(AttributeError):
            _ = value.z

    run_and_rollback("RETURN point({x:3, y:4})", {}, assertion)


def test_cartesian_3d_point_output(run_and_rollback):

    def assertion(data, _):
        value = hydrate_point(*data[0][0])
        assert isinstance(value, CartesianPoint)
        assert value.x == 3.0
        assert value.y == 4.0
        assert value.z == 5.0

    run_and_rollback("RETURN point({x:3, y:4, z:5})", {}, assertion)


def test_wgs84_point_output(run_and_rollback):

    def assertion(data, _):
        value = hydrate_point(*data[0][0])
        assert isinstance(value, WGS84Point)
        assert value.latitude == 3.0
        assert value.y == 3.0
        assert value.longitude == 4.0
        assert value.x == 4.0
        with raises(AttributeError):
            _ = value.height
        with raises(AttributeError):
            _ = value.z

    run_and_rollback("RETURN point({latitude:3, longitude:4})", {}, assertion)


def test_wgs84_3d_point_output(run_and_rollback):

    def assertion(data, _):
        value = hydrate_point(*data[0][0])
        assert isinstance(value, WGS84Point)
        assert value.latitude == 3.0
        assert value.y == 3.0
        assert value.longitude == 4.0
        assert value.x == 4.0
        assert value.height == 5.0
        assert value.z == 5.0

    run_and_rollback("RETURN point({latitude:3, longitude:4, height:5})",
                     {}, assertion)


def test_native_date_input(run_and_rollback):

    def assertion(data, _):
        year, month, day = data[0]
        assert year == 1976
        assert month == 6
        assert day == 13

    value = dehydrate_date(date(1976, 6, 13))
    run_and_rollback("CYPHER runtime=interpreted WITH $x AS x "
                     "RETURN x.year, x.month, x.day", {"x": value}, assertion)


def test_date_input(run_and_rollback):

    def assertion(data, _):
        year, month, day = data[0]
        assert year == 1976
        assert month == 6
        assert day == 13

    value = dehydrate_date(Date(1976, 6, 13))
    run_and_rollback("CYPHER runtime=interpreted WITH $x AS x "
                     "RETURN x.year, x.month, x.day", {"x": value}, assertion)
