#!/usr/bin/env bash

ARGS=$*
VERSIONS="3.4.7 3.3.6 3.2.12"

coverage erase
coverage run -a -m pytest -v ${ARGS} test/unit test/stub #test/performance
if [ -z "NEO4J_SERVER_PACKAGE" ]
then
    for VERSION in ${VERSIONS}
    do
        NEO4J_SERVER_PACKAGE=http://dist.neo4j.org/neo4j-enterprise-${VERSION}-unix.tar.gz coverage run -a -m pytest -v ${ARGS} test/integration
        STATUS="$?"
        if [ "${STATUS}" != "0" ]
        then
            exit ${STATUS}
        fi
    done
else
    coverage run -a -m pytest -v ${ARGS} test/integration
    STATUS="$?"
    if [ "${STATUS}" != "0" ]
    then
        exit ${STATUS}
    fi
fi
coverage report
