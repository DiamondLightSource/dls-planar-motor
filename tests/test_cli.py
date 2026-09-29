import subprocess
import sys

from dls_planar_motor import __version__


def test_cli_version():
    cmd = [sys.executable, "-m", "dls_planar_motor", "--version"]
    assert subprocess.check_output(cmd).decode().strip() == __version__
