# logger.py

Use `StreamToLogger` to monitor all output from applications which should write to a log file rather than an interactive terminal. It will forward `print()` calls, which would otherwise be lost, into the logger.

- **Stream redirection**: The `StreamToLogger` class allows redirection of standard output and error streams to a logging instance.

## Example Usage

### Redirect `stdout` and `stderr` to a logger.

Add this boilerplate code to the top of a Python file. Subsequent `print()` output will redirect to the log file along with output from `log.info()` and `log.warning()`.

*python*

```python
logging.basicConfig(
    filename='output.log',
    format='%(asctime)s %(levelname)s: %(message)s',
    level=logging.INFO
)
log = logging.getLogger(__name__)
sys.stdout = StreamToLogger(log, logging.INFO)
sys.stderr = StreamToLogger(log, logging.ERROR)
```
