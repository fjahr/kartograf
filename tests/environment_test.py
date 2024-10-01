import unittest
import sys
import os
import subprocess
import json
from pathlib import PurePath
from importlib.metadata import distribution

RPKI_VERSION="9.1"
CHECK_MARK = "\U00002705"

class EnvironmentTest(unittest.TestCase):
    def __print_with_format(self, name, version):
        col1 = f"{name} version:"
        col2 = f"{CHECK_MARK} OK"
        print(f"{col1:25} {col2:5} ({version})")

    def test_python_version(self):
        min_version = (3, 10)
        sys_version = sys.version_info
        result = (sys_version >= min_version)
        if result:
            self.__print_with_format("Python", f"{sys_version.major}.{sys_version.minor}")
        self.assertTrue(result)

    def test_rpki_version(self):
        rpki_path = subprocess.check_output(["which",  "rpki-client"])
        derivation = subprocess.check_output(["nix", "derivation", "show", rpki_path])
        derivation_env = json.loads(derivation).values()
        rpki_version = list(derivation_env)[0].get('env').get('version')
        result = (rpki_version == RPKI_VERSION)
        if result:
            self.__print_with_format("RPKI-client", f"{rpki_version}")
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
            # assert that our python packages are in the same Nix store path as the python env
            common_path = os.path.commonpath([dist.locate_file('.'), python_executable_path])
            result = (common_path == python_env_path)
            if result:
               self.__print_with_format(package, dist.version)
            self.assertTrue(result)

if __name__ == "__main__":
    unittest.main(verbosity=0)

