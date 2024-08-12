import subprocess
import sys

from htss_rig_bluesky import __version__


def test_cli_version():
    cmd = [sys.executable, "-m", "htss", "--version"]
    assert subprocess.check_output(cmd).decode().strip() == __version__
