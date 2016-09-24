
import os
import sys
assert sys.version_info >= (3, 4, 0)
import pathlib


ROOT = pathlib.Path(__file__).resolve().parent
LIB_PATH = ROOT / "lib"
LOG_PATH = ROOT / "MBTA.log"
CONFIGS_PATH = ROOT / "configs.csv"

sys.path.append(str(LIB_PATH))
