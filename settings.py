
import os
import sys
assert sys.version_info >= (3, 4, 0)
import pathlib


ROOT = pathlib.Path(__file__).resolve().parent
LIB_PATH = ROOT / "lib"
LOG_PATH = ROOT / "logs"
CONFIG_PATH = ROOT / "configs"

sys.path.append(str(LIB_PATH))
