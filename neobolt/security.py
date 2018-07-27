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


from warnings import warn

from neobolt.compat.ssl import SSL_AVAILABLE, SSLContext, PROTOCOL_SSLv23, OP_NO_SSLv2, CERT_REQUIRED
from neobolt.config import default_config, TRUST_ALL_CERTIFICATES, TRUST_CUSTOM_CA_SIGNED_CERTIFICATES, TRUST_ON_FIRST_USE, TRUST_SIGNED_CERTIFICATES, TRUST_SYSTEM_CA_SIGNED_CERTIFICATES


ENCRYPTION_OFF = 0
ENCRYPTION_ON = 1
ENCRYPTION_DEFAULT = ENCRYPTION_ON if SSL_AVAILABLE else ENCRYPTION_OFF


class AuthToken(object):
    """ Container for auth information
    """

    #: By default we should not send any realm
    realm = None

    def __init__(self, scheme, principal, credentials, realm=None, **parameters):
        self.scheme = scheme
        self.principal = principal
        self.credentials = credentials
        if realm:
            self.realm = realm
        if parameters:
            self.parameters = parameters


class SecurityPlan(object):

    @classmethod
    def build(cls, **config):
        encrypted = config.get("encrypted", default_config["encrypted"])
        if encrypted is None:
            encrypted = _encryption_default()
        trust = config.get("trust", default_config["trust"])
        if encrypted:
            if not SSL_AVAILABLE:
                raise RuntimeError("Bolt over TLS is only available in Python 2.7.9+ and "
                                   "Python 3.3+")
            ssl_context = SSLContext(PROTOCOL_SSLv23)
            ssl_context.options |= OP_NO_SSLv2
            if trust == TRUST_ON_FIRST_USE:
                warn("TRUST_ON_FIRST_USE is deprecated, please use "
                     "TRUST_ALL_CERTIFICATES instead")
            elif trust == TRUST_SIGNED_CERTIFICATES:
                warn("TRUST_SIGNED_CERTIFICATES is deprecated, please use "
                     "TRUST_SYSTEM_CA_SIGNED_CERTIFICATES instead")
                ssl_context.verify_mode = CERT_REQUIRED
            elif trust == TRUST_ALL_CERTIFICATES:
                pass
            elif trust == TRUST_CUSTOM_CA_SIGNED_CERTIFICATES:
                raise NotImplementedError("Custom CA support is not implemented")
            elif trust == TRUST_SYSTEM_CA_SIGNED_CERTIFICATES:
                ssl_context.verify_mode = CERT_REQUIRED
            else:
                raise ValueError("Unknown trust mode")
            ssl_context.set_default_verify_paths()
        else:
            ssl_context = None
        return cls(encrypted, ssl_context, trust != TRUST_ON_FIRST_USE)

    def __init__(self, requires_encryption, ssl_context, routing_compatible):
        self.encrypted = bool(requires_encryption)
        self.ssl_context = ssl_context
        self.routing_compatible = routing_compatible


_warned_about_insecure_default = False


def _encryption_default():
    global _warned_about_insecure_default
    if not SSL_AVAILABLE and not _warned_about_insecure_default:
        warn("Bolt over TLS is only available in Python 2.7.9+ and Python 3.3+ "
             "so communications are not secure")
        _warned_about_insecure_default = True
    return ENCRYPTION_DEFAULT
