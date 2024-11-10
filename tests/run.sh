#!/usr/bin/env bash

SCRIPTPATH="$( cd "$(dirname "$0")" ; pwd -P )"
cd $SCRIPTPATH

cd ..

COMMAND=$1

if [ "$COMMAND" == "full" ]; then
    python -m unittest discover -v
else
    python -m unittest discover
fi