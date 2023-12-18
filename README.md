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

### Publish
    poetry version [major|minor|patch]
    V=v`poetry version -s` && git commit -m $V && git tag -a -m $V $V
    poetry publish --build
