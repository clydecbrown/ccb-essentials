"""Unit tests"""
import os

from _pytest.logging import LogCaptureFixture

from ccb_essentials.subprocess import subprocess_command, shell_escape


class TestSubprocessCommand:
    """Unit tests for subprocess_command()"""

    @staticmethod
    def test_list_files() -> None:
        """It should list files from the filesystem."""
        expected = ["bin", "etc", "tmp"]
        results_str = subprocess_command("ls /")
        assert isinstance(results_str, str)
        results = results_str.split()
        for file in expected:
            assert file in results

    @staticmethod
    def test_fail() -> None:
        """It should fail gracefully on an unknown command."""
        assert subprocess_command("not a command") is None

    @staticmethod
    def test_report_error(caplog: LogCaptureFixture) -> None:
        """It should print stderr from a failed command."""
        assert subprocess_command("not a command") is None
        assert "not found" in caplog.text or "non-zero exit status" in caplog.text

    @staticmethod
    def test_strip() -> None:
        """It should strip whitespace from results."""
        raw = subprocess_command("uptime", strip_output=False)
        assert isinstance(raw, str)
        assert "load average" in raw
        assert raw.endswith(os.linesep)

        stripped = subprocess_command("uptime", strip_output=True)
        assert isinstance(stripped, str)
        assert "load average" in stripped
        assert not stripped.endswith(os.linesep)

    @staticmethod
    def test_shell_escape() -> None:
        """It should escape special characters for use in a shell."""
        for test in [
            ('', '""'),
            ('/', '"/"'),
            ('/foo/test1.txt', '"/foo/test1.txt"'),
            ('/foo/path with whitespace.txt', '"/foo/path with whitespace.txt"'),
            ("""abc"def' `hij""", '''"abc\\"def' \\`hij"'''),
        ]:
            assert shell_escape(test[0]) == test[1]
