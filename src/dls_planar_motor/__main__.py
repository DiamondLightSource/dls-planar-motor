"""Interface for ``python -m dls_planar_motor``."""

from argparse import ArgumentParser
from collections.abc import Sequence

import uvicorn

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
    parser.add_argument(
        "--serve", action="store_true", help="Start the FastAPI control web server"
    )

    parsed_args = parser.parse_args(args)

    if parsed_args.serve:
        print("Starting Control API Server...")
        # Points directly to the app instance inside this current file
        uvicorn.run("dls_planar_motor.api:app", host="0.0.0.0", port=8000)


if __name__ == "__main__":
    main()
