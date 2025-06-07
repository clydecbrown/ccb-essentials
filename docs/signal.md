# signal.py

IPC signal handling tools.

- **Delayed interruptions**: Use `DelayedKeyboardInterrupt` to postpone `KeyboardInterrupt` signals during a critical operation.

## Example Usage

### Prevent a block of code from being interrupted by `KeyboardInterrupt`.

*python*

```python
try:
    with DelayedKeyboardInterrupt():
        print("Start critical operation")
        time.sleep(10)  # Try sending a Ctrl-C here.
        print("End critical operation")
except KeyboardInterrupt:
    print("Operation was interrupted")
```
