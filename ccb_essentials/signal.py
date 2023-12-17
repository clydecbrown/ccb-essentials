"""Signals utils:
https://docs.python.org/3/library/signal.html
"""
import logging
import signal
from typing import Any, Optional, Tuple

log = logging.getLogger(__name__)


# todo tests
class DelayedKeyboardInterrupt:
    """Delay KeyboardInterrupt exception during a critical operation.
    https://stackoverflow.com/questions/842557/how-to-prevent-a-block-of-code-from-being-interrupted-by-keyboardinterrupt-in-py
    """

    def __init__(self) -> None:
        self.signal_received: Optional[Tuple[int, Any]] = None
        self.old_handler: Any = None

    def __enter__(self) -> None:
        self.old_handler = signal.signal(signal.SIGINT, self.handler)

    def handler(self, sig: int, frame: Any) -> None:
        """Signal handler"""
        self.signal_received = (sig, frame)
        log.debug('SIGINT received. Delaying KeyboardInterrupt.')

    def __exit__(self, _type: Any, _value: Any, _traceback: Any) -> None:
        signal.signal(signal.SIGINT, self.old_handler)
        if self.signal_received:
            self.old_handler(*self.signal_received)
