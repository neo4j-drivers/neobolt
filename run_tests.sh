#!/usr/bin/env bash

ARGS=$*
VERSIONS="3.5.0-alpha07 3.4.7 3.3.6 3.2.12"

coverage erase
coverage run -a -m pytest -v ${ARGS} test/unit test/stub #test/performance
STATUS="$?"
if [ ${STATUS} -ne 0 ]
then
    exit ${STATUS}
fi
if [ -z "${NEO4J_SERVER_PACKAGE}" ]
then
    for VERSION in ${VERSIONS}
    do
        echo "Integration testing against Neo4j ${VERSION}"
        NEO4J_SERVER_PACKAGE="http://dist.neo4j.org/neo4j-enterprise-${VERSION}-unix.tar.gz" coverage run -a -m pytest -v ${ARGS} test/integration
        STATUS="$?"
        if [ ${STATUS} -ne 0 ]
        then
            exit ${STATUS}
        fi
    done
else
    echo "Integration testing against Neo4j at ${NEO4J_SERVER_PACKAGE}"
    coverage run -a -m pytest -v ${ARGS} test/integration
    STATUS="$?"
    if [ ${STATUS} -ne 0 ]
    then
        exit ${STATUS}
    fi
fi
coverage report
