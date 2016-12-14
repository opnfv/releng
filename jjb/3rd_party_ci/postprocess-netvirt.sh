#!/bin/bash
set -e

# wipe the WORKSPACE
if [ -z ${WORKSPACE} ]; then echo "WORKSPACE is unset"; else echo "WORKSPACE is set to \"$WORKSPACE\""; fi
WORKSPACE=${WORKSPACE:-$PWD}
/bin/rm -rf $WORKSPACE/*

echo "Hello World"