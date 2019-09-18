#!/bin/bash

set -ev

# Environment checks
if [ "$PIP" == "" ]; then
  export PIP='python -m pip'
fi

# Repository root path
REPO_ROOT="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )/.."
echo "Install Linux packages from $REPO_ROOT"

# Install Python libraries
$PIP install --upgrade pip setuptools tox-travis 
$PIP install -r "$REPO_ROOT/requirements.dev.txt"

