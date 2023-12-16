"""Argparse helpers"""
import argparse


def str2bool(s: str) -> bool:
    """Interpret input string as a boolean.
    Use this with argparse for more user-friendly boolean inputs."""
    if s.lower() in ('1', 'true', 't', 'yes', 'y'):
        return True
    if s.lower() in ('0', 'false', 'f', 'no', 'n'):
        return False
    raise argparse.ArgumentTypeError(f"boolean value expected, not {type(s)}: '{s}'")
