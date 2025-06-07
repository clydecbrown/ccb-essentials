"""Unit tests"""
import logging
import os
import sys
from tempfile import NamedTemporaryFile

from _pytest.capture import CaptureFixture
from _pytest.logging import LogCaptureFixture

from ccb_essentials.filesystem import real_path
from ccb_essentials.logger import StreamToLogger


def _expand(path: str) -> str:
    return os.path.realpath(os.path.expanduser(path))


class TestStreamToLogger:
    """Unit tests for StreamToLogger"""

    @staticmethod
    def test_redirect(capsys: CaptureFixture[str], caplog: LogCaptureFixture) -> None:
        """It should redirect printed output to the logger."""
        caplog.set_level(logging.DEBUG)  # capture all levels
        with NamedTemporaryFile() as f:
            # This block is an example of typical usage, somewhere near the top of a script
            # which needs to redirect all output to a file:
            logging.basicConfig(
                filename=real_path(f.name, check_exists=False),
                format='%(asctime)s %(levelname)s: %(message)s',
                level=logging.INFO
            )
            log = logging.getLogger(__name__)
            sys.stdout = StreamToLogger(log, logging.INFO)
            sys.stderr = StreamToLogger(log, logging.ERROR)

            log.info("test log.info message.")
            log.error("test log.error message.")
            print("test print stdout message.", file=sys.stdout, flush=True)
            print("test print stderr message.", file=sys.stderr, flush=True)
            captured = capsys.readouterr()

            assert "test log.info message." in caplog.text
            assert "test log.error message." in caplog.text

            assert "test print stdout message." in caplog.text
            assert "test print stderr message." in caplog.text
            assert "test print stdout message." not in captured.out
            assert "test print stderr message." not in captured.err

            assert "not printed" not in caplog.text
            assert "not printed" not in captured.out
            assert "not printed" not in captured.err

    @staticmethod
    def test_print(capsys: CaptureFixture[str], caplog: LogCaptureFixture) -> None:
        """Sanity check: it should not redirect printed output if not asked."""
        caplog.set_level(logging.DEBUG)  # capture all levels
        with NamedTemporaryFile() as f:
            logging.basicConfig(
                filename=real_path(f.name, check_exists=False),
                format='%(asctime)s %(levelname)s: %(message)s',
                level=logging.INFO
            )
            log = logging.getLogger(__name__)

            log.info("test log.info message.")
            log.error("test log.error message.")
            print("test print stdout message.", file=sys.stdout, flush=True)
            print("test print stderr message.", file=sys.stderr, flush=True)
            captured = capsys.readouterr()

            assert "test log.info message." in caplog.text
            assert "test log.error message." in caplog.text

            assert "test print stdout message." not in caplog.text
            assert "test print stderr message." not in caplog.text
            assert "test print stdout message." in captured.out
            assert "test print stderr message." in captured.err

            assert "not printed" not in caplog.text
            assert "not printed" not in captured.out
            assert "not printed" not in captured.err
