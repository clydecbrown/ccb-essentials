"""Unit tests"""
import argparse

from ccb_essentials.argparse import str2bool

_truthy = ['1', 'true', 'True', 't', 'T', 'yes', 'Yes', 'y', 'Y']
_falsy = ['0', 'false', 'False', 'f', 'F', 'no', 'No', 'n', 'N']
_input_expected = list(zip(_truthy, [True] * len(_truthy))) + \
                  list(zip(_falsy, [False] * len(_falsy)))


class TestStr2Bool:
    """Unit tests for str2bool()"""

    @staticmethod
    def test_str2bool() -> None:
        """It should interpret truthy strings as True and falsy strings as False."""
        for string, expected in _input_expected:
            assert str2bool(string) == expected

    @staticmethod
    def test_argparse() -> None:
        """It should provide the correct boolean when applied to argparse."""
        parser = argparse.ArgumentParser()
        parser.add_argument("--test_bool", type=str2bool)
        for string, expected in _input_expected:
            assert parser.parse_args(["--test_bool", string]).test_bool == expected
