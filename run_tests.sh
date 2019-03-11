#!/usr/bin/env bash

ARGS=$*
VERSIONS="3.5.3 3.4.12 3.3.9"

coverage erase

echo "Running unit tests"
coverage run -a -m pytest -v ${ARGS} test/unit
STATUS="$?"
if [[ ${STATUS} -ne 0 ]]
then
    exit ${STATUS}
fi

echo "Running stub tests"
coverage run -a -m pytest -v ${ARGS} test/stub
STATUS="$?"
if [[ ${STATUS} -ne 0 ]]
then
    exit ${STATUS}
fi

if [[ -z "${NEO4J_SERVER_PACKAGE}" ]]
then
    for VERSION in ${VERSIONS}
    do
        echo "Running integration tests against Neo4j ${VERSION}"
        NEO4J_SERVER_PACKAGE="http://dist.neo4j.org/neo4j-enterprise-${VERSION}-unix.tar.gz" coverage run -a -m pytest -v ${ARGS} test/integration
        STATUS="$?"
        if [[ ${STATUS} -ne 0 ]]
        then
            exit ${STATUS}
        fi
    done
else
    echo "Running integration tests against Neo4j at ${NEO4J_SERVER_PACKAGE}"
    coverage run -a -m pytest -v ${ARGS} test/integration
    STATUS="$?"
    if [[ ${STATUS} -ne 0 ]]
    then
        exit ${STATUS}
    fi
fi

coverage report
