# Python Essentials

General-purpose tools for Python 3.

## Development Environment

First, [install Poetry](https://python-poetry.org/docs/).

### Set up
    poetry install --sync
    poetry check
    poetry show

## Maintenance

### Code test
    poetry run pytest

### Code lint
    poetry run bin/lint.sh

### Build artifacts
    poetry build
