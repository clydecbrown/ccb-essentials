#!/bin/bash
# Clean all the code.

# https://mypy.readthedocs.io/en/latest/
# https://pylint.readthedocs.io/en/latest/
# http://pycodestyle.pycqa.org/en/latest/intro.html

set -e

SOURCES="ccb_essentials tests"

GREEN='\033[0;32m'
NC='\033[0m'

echo "mypy:" && \
mypy --pretty $SOURCES && \
echo "pylint:" && \
pylint $SOURCES && \
echo "pycodestyle:" && \
pycodestyle --max-line-length=120 $SOURCES && \
printf "${GREEN}This code is clean.${NC}\n"
