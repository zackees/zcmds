#!/bin/bash
set -e
# cd to self bash script directory
cd $( dirname ${BASH_SOURCE[0]})
echo Running flake8 src
flake8 src
echo Running pylint src
pylint src
echo Running mypy src
mypy src
echo Linting complete!