# filesystem.py

Utilities for filesystem paths. `real_path()` and the `assert_real*` functions associate a Python `Path` with a real path on the host's filesystem. These terse commands quickly sanitize inputs, eliminating boilerplate code. They are essential for any application that works with the filesystem.

Additional helper functions create temporary files, pretty-print a directory tree structure, and perform comparisons on directory trees.

## Example Usage

### Expand a path, and verify that it exists.

`real_path()` automatically applies `os.path.realpath()` and `os.path.expanduser()`. It returns `None` if the expanded path does not exist.

*python*

```python
home_path = real_path('~')
print(type(home_path), home_path.is_dir())  # <class 'pathlib.PosixPath'> True
```

### Assert that a path is a file.

*python*

```python
file_path = assert_real_file('/usr/bin/less')
print(type(file_path), file_path)  # <class 'pathlib.PosixPath'> /usr/bin/less
```

### Reduce the boilerplate code for parsing program arguments.

If the input arguments are not valid, the program will halt with an exception before the inputs can cause a real problem. As a convenience, create the input directory if it does not exist.

*python*

```python
parser = argparse.ArgumentParser()
parser.add_argument('input_dir_path', type=str)
args = parser.parse_args()
validated_path = assert_real_dir(args.input_dir_path, mkdir=True)
print(type(validated_path), validated_path.is_dir())  # <class 'pathlib.PosixPath'> True
```

The call to `assert_real_dir()` replaces the following:

*python*

```python
input_dir_path = args.input_dir_path
real = pathlib.Path(os.path.realpath(os.path.expanduser(input_dir_path)))
real.mkdir(parents=True, exist_ok=True)
if not real.is_dir():
    raise NotADirectoryError(f'path {real} is not a directory')
```

### Create a Path to a temporary file with a known name.

Use this if you need a reliable temporary file and also need to control its name.

*python*

```python
with temporary_path(name="xyz", touch=True) as path:
    print(type(path), path.is_file(), path.name)  # <class 'pathlib.PosixPath'> True xyz
```

### Pretty-print a directory tree.

*python*

```python
for line in tree('/usr/share/vim'):
    print(line)
```

*output*

```
vim
├── vim90
│   ├── autoload
│   │   ├── README.txt
...
│   └── vimrc_example.vim
└── vimrc
```

### Compare the roots of directories.

`common_root()`, `common_ancestor()`, and `common_parent()` find the path components in common between two or more input paths. See the descriptions below for details.

*python*

```python
paths = map(real_path, ['/bin/echo', '/bin/kill', '/bin/ls', '/bin/mv'])
print(common_ancestor(paths))  # /bin
```

## Function Descriptions

### Path Sanitizing

- **`real_path`**: Cleans and verifies the existence of a path.
  - **Parameters**:
    - `path` (str or Path): Filesystem path.
    - `check_exists` (bool): Check if the path exists.
    - `mkdir` (bool): Create the path if it is meant to be a directory and if it does not exist.
  - **Returns**: The real path as a `Path` object or `None` if the path does not exist.

- **`assert_real_path`**: Cleans a path and asserts its existence.
  - **Parameters**:
    - `path` (str or Path): Filesystem path.
    - `mkdir` (bool): Create the directory if it does not exist.
  - **Returns**: The real path as a `Path` object.
  - **Raises**: `FileNotFoundError` if the path does not exist.

- **`assert_real_file`**: Cleans a path and asserts that it is a file.
  - **Parameters**: `path` (str or Path): Filesystem path.
  - **Returns**: The real path as a `Path` object.
  - **Raises**: `OSError` if the path is not a file.

- **`assert_real_dir`**: Cleans a path and asserts that it is a directory.
  - **Parameters**:
    - `path` (str or Path): Filesystem path.
    - `mkdir` (bool): Create the directory if it does not exist.
  - **Returns**: The real path as a `Path` object.
  - **Raises**: `NotADirectoryError` if the path is not a directory.

### Temporary Path

- **`temporary_path`**: Creates a temporary file with a known name.
  - **Parameters**:
    - `name` (str): Name of the file.
    - `touch` (bool): Create the file on the filesystem.
  - **Returns**: A generator yielding the temporary `Path` object.

### Directory Tree

- **`tree`**: Generates a pretty-printable directory tree.
  - **Parameters**:
    - `root` (str or Path): Root directory to generate the tree from.
    - `prefix` (str): Prefix to use for indentation, typically some white space.
  - **Returns**: A generator yielding strings representing the directory tree.

### Common Directories and Parents

- **`common_root`**: Finds the deepest common directory between two paths.
  - **Parameters**: `a` (Path) and `b` (Path): Two paths to compare.
  - **Returns**: The deepest common directory as a `Path` object or `None` if not found.

- **`common_ancestor`**: Finds the deepest directory common to all given paths.
  - **Parameters**: `paths` (Iterable[Path]): Two or more paths to compare.
  - **Returns**: The deepest common directory as a `Path` object or `None` if not found.

- **`common_parent`**: Finds the immediate parent directory shared by all given paths.
  - **Parameters**: `paths` (Iterable[Path]): Two or more paths to compare.
  - **Returns**: The immediate parent directory as a `Path` object or `None` if not found.

