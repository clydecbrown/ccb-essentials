"""Signals utils:
https://docs.python.org/3/library/signal.html
"""
import logging
import signal

log = logging.getLogger(__name__)


# todo tests
# todo types
class DelayedKeyboardInterrupt:
    """Delay KeyboardInterrupt exception during a critical operation.
    https://stackoverflow.com/questions/842557/how-to-prevent-a-block-of-code-from-being-interrupted-by-keyboardinterrupt-in-py
    """

    def __init__(self):
        self.signal_received = None

    def __enter__(self):
        self.old_handler = signal.signal(signal.SIGINT, self.handler)

    def handler(self, sig, frame):
        self.signal_received = (sig, frame)
        log.debug('SIGINT received. Delaying KeyboardInterrupt.')

    def __exit__(self, type, value, traceback):
        signal.signal(signal.SIGINT, self.old_handler)
        if self.signal_received:
            self.old_handler(*self.signal_received)
