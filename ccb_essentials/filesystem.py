"""Filesystem helpers"""
import logging
import os
from contextlib import contextmanager
from pathlib import Path
from tempfile import TemporaryDirectory
from typing import Optional, Union, Generator, Iterable

log = logging.getLogger(__name__)


def real_path(path: Union[str, Path], check_exists: bool = True, mkdir: bool = False) -> Optional[Path]:
    """Clean `path` and verify that it exists."""
    path = str(path)
    real = Path(os.path.realpath(os.path.expanduser(path)))

    if not check_exists:
        return real

    if real.exists():
        return real

    if mkdir:
        log.debug("creating directory %s", str(real))
        real.mkdir(parents=True)
        return real

    return None


def assert_real_path(path: Union[str, Path], mkdir: bool = False) -> Path:
    """Clean `path` and assert that it exists."""
    new_path = real_path(path, check_exists=True, mkdir=mkdir)
    if new_path is None:
        raise FileNotFoundError("path %s does not exist" % path)
    return new_path


def assert_real_file(path: Union[str, Path]) -> Path:
    """Clean `path` and assert that it is a file."""
    new_path = assert_real_path(path)
    if not new_path.is_file():
        raise OSError("path %s is not a file" % path)
    return new_path


def assert_real_dir(path: Union[str, Path], mkdir: bool = False) -> Path:
    """Clean `path` and assert that it is a directory."""
    new_path = assert_real_path(path, mkdir)
    if not new_path.is_dir():
        raise NotADirectoryError("path %s is not a directory" % path)
    return new_path


# todo NamedTemporaryFile
#   or Path(mktemp(dir=dest.parent, prefix=dest.name))
@contextmanager
def temporary_path(name: str = "temp", touch: bool = False) -> Generator[Path, None, None]:
    """Create a path to a temporary file. This differs from tempfile.TemporaryFile()
    which creates a file-like object with no name."""
    if name == "":
        raise ValueError("can't create a temporary_path with no name")
    with TemporaryDirectory() as td:
        path = Path(td) / name
        if touch:
            path.touch()
        yield path


_space = '    '
_branch = '│   '
_tee = '├── '
_last = '└── '


def tree(root: Union[str, Path], prefix: str = '') -> Generator[str, None, None]:
    """Build a pretty-printable directory tree. Example usage:
    print(os.linesep.join(tree(path)))
    """
    if not isinstance(root, Path):
        root = assert_real_path(root)
    if not root.is_dir():
        yield root.name
    else:
        if prefix == '':
            yield root.name
        contents = sorted(root.iterdir())
        lc1 = len(contents) - 1
        for i, path in enumerate(contents):
            pointer = _tee if i < lc1 else _last
            yield prefix + pointer + path.name
            if path.is_dir():
                extension = _branch if i < lc1 else _space
                yield from tree(path, prefix=prefix+extension)


def common_root(a: Path, b: Path) -> Optional[Path]:
    """Find the deepest common directory."""
    if not a.is_absolute() or not b.is_absolute():
        return None
    if a.is_dir():
        a /= 'x'
    if b.is_dir():
        b /= 'x'
    a_parents = list(reversed(a.parents))
    b_parents = list(reversed(b.parents))
    root = Path()
    for n in range(min(len(a_parents), len(b_parents))):
        if a_parents[n] == b_parents[n]:
            root = a_parents[n]
        else:
            break
    return root


def common_ancestor(paths: Iterable[Path]) -> Optional[Path]:
    """Return the deepest directory common to all `paths`."""
    common = None
    for path in paths:
        if not path.is_dir():
            path = path.parent
        if common is None:
            common = path
        elif common != path:
            common = common_root(common, path)
            if common is None:
                return None
    return common


def common_parent(paths: Iterable[Path]) -> Optional[Path]:
    """Return the immediate parent directory, if all `paths` share a common parent."""
    common = None
    for path in paths:
        if common is None:
            common = path.parent
        elif common != path.parent:
            return None
    return common


if __name__ == '__main__':
    for test in [
        ('/', '/', '/'),
        ('/', '/bin/echo', '/'),
        ('/bin/echo', '/', '/'),
        ('/usr/local', '/usr/local/bin/bbedit', '/usr/local'),
        ('/usr/local/bin/bbedit', '/usr/local', '/usr/local'),
        ('/usr/local/bin/bbedit', '/usr/local/bin/bbedit', '/usr/local/bin'),
        ('/usr/local/bin/bbedit', '/usr/bin/Rez', '/usr'),
        ('/usr/bin/Rez', '/usr/local/bin/bbedit', '/usr'),
        ('/usr/local/bin', '/usr/bin', '/usr'),
        ('/usr/bin', '/usr/local/bin', '/usr'),
    ]:
        assert common_root(assert_real_path(test[0]), assert_real_path(test[1])) == assert_real_path(test[2])
        assert common_ancestor((assert_real_path(test[0]), assert_real_path(test[1]))) == assert_real_path(test[2])

    for test in [
        [None],
        [Path('/'), '/'],
        [Path('/'), '/', '/'],
        [Path('/bin'), '/bin'],
        [Path('/bin'), '/bin', '/bin'],
        [Path('/bin'), '/bin/echo', '/bin/kill', '/bin/ls', '/bin/mv'],
        [Path('/usr'), '/usr/lib/dyld', '/usr/local/etc/fonts', '/usr/local/bin/bbedit'],
        [Path('/'), '/bin/echo', '/bin/kill', '/usr/local/bin/bbedit'],
        [Path('/'), '/bin/echo', '/usr/local/bin/bbedit', '/bin/kill'],
        [Path('/'), '/usr/local/bin/bbedit', '/bin/echo', '/bin/kill'],
    ]:
        assert common_ancestor(map(lambda p: assert_real_path(p), test[1:])) == test[0]

    for test in [
        [None],
        [Path('/'), '/'],
        [Path('/'), '/', '/'],
        [Path('/'), '/bin'],
        [Path('/'), '/bin', '/bin'],
        [Path('/bin'), '/bin/echo', '/bin/kill', '/bin/ls', '/bin/mv'],
        [None, '/usr/lib/dyld', '/usr/local/etc/fonts', '/usr/local/bin/bbedit'],
        [None, '/bin/echo', '/bin/kill', '/usr/local/bin/bbedit'],
        [None, '/bin/echo', '/usr/local/bin/bbedit', '/bin/kill'],
        [None, '/usr/local/bin/bbedit', '/bin/echo', '/bin/kill'],
    ]:
        assert common_parent(map(lambda p: assert_real_path(p), test[1:])) == test[0]
