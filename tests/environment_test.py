import unittest
import sys
import os
import subprocess
import json
from pathlib import PurePath
from importlib.metadata import distribution

RPKI_VERSION="9.3"
CHECK_MARK = "\U00002705"
CROSS_MARK = "\U0000274C"

class EnvironmentTest(unittest.TestCase):
    def __print_with_format(self, name, version, success):
        col1 = f"{name} version:"
        col2 = f"{CHECK_MARK} OK" if success else f"{CROSS_MARK}"
        return print(f"{col1:25} {col2:5} ({version})")

    def __get_rpki_version(self):
        rpki_path = subprocess.check_output(["which",  "rpki-client"])
        derivation = subprocess.check_output(["nix", "derivation", "show", rpki_path])
        derivation_env = json.loads(derivation).values()
        rpki_version = list(derivation_env)[0].get('env').get('version')
        return rpki_version

    def test_python_version(self):
        min_version = (3, 10)
        sys_version = sys.version_info
        result = (sys_version >= min_version)
        self.__print_with_format("Python", f"{sys_version.major}.{sys_version.minor}", result)
        self.assertTrue(result)

    def test_rpki_version(self):
        rpki_version = self.__get_rpki_version()
        result = (rpki_version == RPKI_VERSION)
        self.__print_with_format("RPKI-client", f"{rpki_version}", result)
        self.assertTrue(result)

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
            common_path = os.path.commonpath([dist.locate_file('.'), python_executable_path])
            result = (common_path == python_env_path)
            self.__print_with_format(package, dist.version, result)
            self.assertTrue(result)

if __name__ == "__main__":
    unittest.main(verbosity=0)

