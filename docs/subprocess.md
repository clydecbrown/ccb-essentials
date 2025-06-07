# subprocess.py

Easily run a subprocess and capture the result.

The `subprocess_command` function wraps Python's `subprocess.run()` with sensible defaults to run a command and to control how results and errors are reported.

## Example Usage

### Assemble a command-line string.

`shell_escape()` escapes a path string for safe use in shell commands.

*python*

```python
path = "/path/to/somewhere with spaces"
escaped_path = shell_escape(path)
cmd = f"ls {escaped_path}"
print(cmd)  # ls "/path/to/somewhere with spaces"
```

### Run a shell command.

*python*

```python
output = subprocess_command("echo Hello, World!")
print(output)  # Hello, World!
```

### Handle errors.

`subprocess_command()` does not raise `CalledProcessError` by default. On a failed shell command, the function returns `None`. Output from the shell's `stderr` is logged to the Python process's `stderr`.

*python*

```python
cmd = f"ls {shell_escape("/path/to/somewhere with spaces")}"
output = subprocess_command(cmd)
print(output)
```

*stdout*

```shell
None
```

*stderr*

```shell
Command 'ls "/path/to/somewhere with spaces"' returned non-zero exit status 1.
ls: /path/to/somewhere with spaces: No such file or directory
```

## subprocess_command() Description

Input is a command-line string. Output, if all went well, is the standard output of the command as a UTF-8 string.

### Parameters
- `cmd` (str): The shell command to run.
- `report_process_error` (bool): Logs errors if the subprocess command fails.
- `report_std_error` (bool): Logs standard error output.
- `raise_std_error` (bool): Raises a `CalledProcessError` if the subprocess command fails.
- `strip_output` (bool): Strips leading and trailing whitespace from the output.
- `**kwargs`: Additional arguments to pass to `subprocess.run`.

### Returns
- `Optional[str]`: The standard output of the command, or `None` if an error occurs.
