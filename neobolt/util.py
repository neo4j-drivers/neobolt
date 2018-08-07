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


from importlib import import_module
from os import getenv as getenv
from warnings import warn


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


def import_best(c_module, py_module):
    pure_python = getenv("PURE_PYTHON", "")
    if pure_python:
        return import_module(py_module)
    else:
        try:
            return import_module(c_module)
        except ImportError:
            return import_module(py_module)


def deprecated(message):
    """ Decorator for deprecating functions and methods.

    ::

        @deprecated("'foo' has been deprecated in favour of 'bar'")
        def foo(x):
            pass

    """
    def f__(f):
        def f_(*args, **kwargs):
            warn(message, category=DeprecationWarning, stacklevel=2)
            return f(*args, **kwargs)
        f_.__name__ = f.__name__
        f_.__doc__ = f.__doc__
        f_.__dict__.update(f.__dict__)
        return f_
    return f__
