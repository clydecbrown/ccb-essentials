"""Filesystem helpers"""
import logging
import os
from contextlib import contextmanager
from pathlib import Path
from tempfile import TemporaryDirectory
from typing import Optional, Union, Generator, Iterable, List, Tuple

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
        raise FileNotFoundError(f'path {path} does not exist')
    return new_path


def assert_real_file(path: Union[str, Path]) -> Path:
    """Clean `path` and assert that it is a file."""
    new_path = assert_real_path(path)
    if not new_path.is_file():
        raise OSError(f'path {path} is not a file')
    return new_path


def assert_real_dir(path: Union[str, Path], mkdir: bool = False) -> Path:
    """Clean `path` and assert that it is a directory."""
    new_path = assert_real_path(path, mkdir)
    if not new_path.is_dir():
        raise NotADirectoryError(f'path {path} is not a directory')
    return new_path


@contextmanager
def temporary_path(name: str = "temp", touch: bool = False) -> Generator[Path, None, None]:
    """Create a Path to a temporary file with a known name. This differs from
    tempfile.TemporaryFile() which creates a file-like object and
    tempfile.NamedTemporaryFile() which produces a random file name."""
    if name == "":
        raise ValueError("can't create a temporary_path with no name")
    with TemporaryDirectory() as td:
        path = Path(td) / name
        if touch:
            path.touch()
        yield path


_SPACE = '    '
_BRANCH = '│   '
_TEE = '├── '
_LAST = '└── '


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
            pointer = _TEE if i < lc1 else _LAST
            yield prefix + pointer + path.name
            if path.is_dir():
                extension = _BRANCH if i < lc1 else _SPACE
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
    # todo unit tests
    for test1 in [
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
        assert common_root(assert_real_path(test1[0]), assert_real_path(test1[1])) == assert_real_path(test1[2])
        assert common_ancestor((assert_real_path(test1[0]), assert_real_path(test1[1]))) == assert_real_path(test1[2])

    test2: Tuple[Optional[Path], List[str]]
    for test2 in [
        (None, list([])),
        (Path('/'), list(['/'])),
        (Path('/'), list(['/', '/'])),
        (Path('/bin'), list(['/bin'])),
        (Path('/bin'), list(['/bin', '/bin'])),
        (Path('/bin'), list(['/bin/echo', '/bin/kill', '/bin/ls', '/bin/mv'])),
        (Path('/usr'), list(['/usr/lib/dyld', '/usr/local/etc/fonts', '/usr/local/bin/bbedit'])),
        (Path('/'), list(['/bin/echo', '/bin/kill', '/usr/local/bin/bbedit'])),
        (Path('/'), list(['/bin/echo', '/usr/local/bin/bbedit', '/bin/kill'])),
        (Path('/'), list(['/usr/local/bin/bbedit', '/bin/echo', '/bin/kill'])),
    ]:
        assert common_ancestor(map(assert_real_path, test2[1])) == test2[0]

    test3: Tuple[Optional[Path], List[str]]
    for test3 in [
        (None, list([])),
        (Path('/'), list(['/'])),
        (Path('/'), list(['/', '/'])),
        (Path('/'), list(['/bin'])),
        (Path('/'), list(['/bin', '/bin'])),
        (Path('/bin'), list(['/bin/echo', '/bin/kill', '/bin/ls', '/bin/mv'])),
        (None, list(['/usr/lib/dyld', '/usr/local/etc/fonts', '/usr/local/bin/bbedit'])),
        (None, list(['/bin/echo', '/bin/kill', '/usr/local/bin/bbedit'])),
        (None, list(['/bin/echo', '/usr/local/bin/bbedit', '/bin/kill'])),
        (None, list(['/usr/local/bin/bbedit', '/bin/echo', '/bin/kill'])),
    ]:
        assert common_parent(map(assert_real_path, test3[1])) == test3[0]
