"""Logging utilities."""
import io
from logging import Logger
from types import TracebackType
from typing import TextIO, BinaryIO, Iterable, AnyStr, Iterator, List, Optional


class StreamToLogger(TextIO):
    """File-like stream object that redirects writes to a logger instance.
    https://stackoverflow.com/questions/19425736/how-to-redirect-stdout-and-stderr-to-logger-in-python
    """
    def __init__(self, logger: Logger, level: int) -> None:
        self.logger = logger
        self.level = level

    def write(self, s: str) -> int:
        """Write to the logger."""
        written = 0
        for line in s.rstrip().splitlines():
            printed = line.rstrip()
            self.logger.log(self.level, printed)
            written += len(printed)   # doesn't include the logger's formatting
        return written

    @property
    def buffer(self) -> BinaryIO:
        """Not implemented."""
        return io.BytesIO()

    def close(self) -> None:
        """Not implemented."""
        return None

    @property
    def encoding(self) -> str:
        """Not implemented."""
        return ''

    @property
    def errors(self) -> None:
        """Not implemented."""
        return None

    def flush(self) -> None:
        """Not implemented."""
        return None

    def fileno(self) -> int:
        """Not implemented."""
        return 0

    def isatty(self) -> bool:
        """Not implemented."""
        return False

    @property
    def line_buffering(self) -> int:
        """Not implemented."""
        return 0

    @property
    def newlines(self) -> None:
        """Not implemented."""
        return None

    # pylint: disable-next=unused-argument
    def read(self, n: int = -1, /) -> AnyStr:  # type: ignore[type-var]
        """Not implemented."""
        return ''  # type: ignore[return-value]

    def readable(self) -> bool:
        """Not implemented."""
        return False

    # pylint: disable-next=unused-argument
    def readline(self, limit: int = -1, /) -> AnyStr:  # type: ignore[type-var]
        """Not implemented."""
        return ''  # type: ignore[return-value]

    # pylint: disable-next=unused-argument
    def readlines(self, hint: int = -1, /) -> List[AnyStr]:
        """Not implemented."""
        return []

    # pylint: disable-next=unused-argument
    def seek(self, offset: int, whence: int = 0, /) -> int:
        """Not implemented."""
        return 0

    def seekable(self) -> bool:
        """Not implemented."""
        return False

    def tell(self) -> int:
        """Not implemented."""
        return 0

    # pylint: disable-next=unused-argument
    def truncate(self, size: Optional[int] = None, /) -> int:
        """Not implemented."""
        return 0

    def writable(self) -> bool:
        """Not implemented."""
        return True

    # pylint: disable-next=unused-argument
    def writelines(self, lines: Iterable[str], /) -> None:
        """Not implemented."""
        return None

    def __next__(self) -> AnyStr:  # type: ignore[type-var]
        """Not implemented."""
        return ''  # type: ignore[return-value]

    def __iter__(self) -> Iterator[AnyStr]:
        """Not implemented."""
        return iter(())

    def __enter__(self) -> TextIO:
        """Not implemented."""
        return self

    # pylint: disable-next=unsupported-binary-operation
    def __exit__(self, t: type[BaseException] | None, value: BaseException | None, traceback: TracebackType | None, /)\
            -> None:
        """Not implemented."""
        return None
