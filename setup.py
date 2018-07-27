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


from __future__ import print_function

from os.path import dirname, join as path_join
try:
    from setuptools import setup, Extension
except ImportError:
    from distutils.core import setup, Extension

from neobolt.meta import version

try:
    from Cython.Build import cythonize
    from Cython.Distutils import build_ext
except ImportError:
    ext_modules = [
        Extension("neobolt.bolt._io", ["neobolt/bolt/_io.c"]),
        Extension("neobolt.packstream._packer", ["neobolt/packstream/_packer.c"]),
        Extension("neobolt.packstream._unpacker", ["neobolt/packstream/_unpacker.c"]),
    ]
else:
    ext_modules = cythonize([Extension("*", ["**/*.pyx"])])

install_requires = [
]
classifiers = [
    "Intended Audience :: Developers",
    "License :: OSI Approved :: Apache Software License",
    "Operating System :: OS Independent",
    "Topic :: Database",
    "Topic :: Software Development",
    "Programming Language :: Python :: 2.7",
    "Programming Language :: Python :: 3.4",
    "Programming Language :: Python :: 3.5",
    "Programming Language :: Python :: 3.6",
    "Programming Language :: Python :: 3.7",
]
packages = [
    "neobolt",
    "neobolt.bolt",
    "neobolt.compat",
    "neobolt.packstream",
]
package_data = {
    "neobolt.bolt": ["*.pyx"],
    "neobolt.packstream": ["*.pyx"],
}
setup_args = {
    "name": "neobolt",
    "version": version,
    "description": "Neo4j Bolt connector for Python",
    "license": "Apache License, Version 2.0",
    "long_description": open(path_join(dirname(__file__), "README.rst")).read(),
    "author": "Neo4j Sweden AB",
    "author_email": "drivers@neo4j.com",
    "keywords": "neo4j graph database",
    "url": "https://github.com/neo4j-drivers/neobolt",
    "install_requires": install_requires,
    "classifiers": classifiers,
    "packages": packages,
    "ext_modules": ext_modules,
}

try:
    setup(**setup_args)
except SystemExit:
    print("Compilation failed, falling back to pure Python.")
    del setup_args["ext_modules"]
    setup(**setup_args)
