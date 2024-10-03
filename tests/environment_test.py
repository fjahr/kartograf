import unittest
import sys
import os
import subprocess
import json
from kartograf.util import (get_rpki_wanted_version, get_rpki_local_version)
from pathlib import PurePath
from importlib.metadata import distribution

CHECK_MARK = "\U00002705"
CROSS_MARK = "\U0000274C"


class EnvironmentTest(unittest.TestCase):
    def __print_with_format(self, name, version, success, error_msg=None):
        col1 = f"{name} version:"
        col2 = f"{CHECK_MARK} OK" if success else f"{CROSS_MARK}"
        col3 = "" if success else f"{error_msg}"
        return print(f"{col1:25} {col2:5} ({version}) {col3}")

    def test_python_version(self):
        min_version = (3, 10)
        sys_version = sys.version_info
        result = (sys_version >= min_version)
        self.__print_with_format(
            "Python",
            f"{sys_version.major}.{sys_version.minor}",
            result)
        self.assertTrue(result)

    def test_rpki_version(self):
        wanted_rpki_version = get_rpki_wanted_version()
        local_rpki_version = get_rpki_local_version()
        result = (wanted_rpki_version == local_rpki_version)
        if result:
            self.__print_with_format(
                "RPKI-client", f"{local_rpki_version}", result)
        elif wanted_rpki_version is None:
            self.__print_with_format(
                "RPKI-client",
                f"{local_rpki_version}",
                result,
                f"Latest version wasn't found. Is Nix installed?")
        else:
            self.__print_with_format(
                "RPKI-client",
                f"{local_rpki_version}",
                result,
                f"want v{wanted_rpki_version}")

    def test_installed_packages(self):
        python_executable_path = PurePath(sys.executable)
        python_env_path = python_executable_path.parents[1].as_posix()
        required_packages = {
            "numpy": "1.26.4",
            "pandas": "1.5.3",
            "beautifulsoup4": "4.11.1",
            "requests": "2.31.0",
            "tqdm": "4.66.3",
            "pandarallel": "1.6.5"
        }
        for package, min_version in required_packages.items():
            dist = distribution(package)
            # assert that our package versions meet requirements
            self.assertGreaterEqual(dist.version, min_version)
            # assert that our python packages are in the python env (the project Nix store path)
            common_path = os.path.commonpath(
                [dist.locate_file('.'), python_executable_path])
            result = (common_path == python_env_path)
            self.__print_with_format(package, dist.version, result)
            self.assertTrue(result)


if __name__ == "__main__":
    unittest.main(verbosity=0)
