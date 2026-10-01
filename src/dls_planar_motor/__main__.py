"""Interface for ``python -m dls_planar_motor``."""

from argparse import ArgumentParser
from collections.abc import Sequence

from dls_planar_motor.ping_plc import PingPLC

from . import __version__

__all__ = ["main"]


def main(args: Sequence[str] | None = None) -> None:
    """Argument parser for the CLI."""
    parser = ArgumentParser()
    parser.add_argument(
        "-v",
        "--version",
        action="version",
        version=__version__,
    )
    parser.add_argument(
        "-p",
        "--ping",
        action=PingPLC,
    )
    parser.parse_args(args)


if __name__ == "__main__":
    main()
