
import argparse
import json
import sys

from . import errors
from . import settings


def stdout(strng):
    sys.stdout.write("{}\n".format(strng))
    sys.stdout.flush()


def stderr(strng):
    sys.stderr.write("{}\n".format(strng))
    sys.stderr.flush()


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("config", help="The config file name to use")
    return parser.parse_args()


def load_config(config_name):
    try:
        config_path = str(settings.CONFIG_PATH / "{}.json".format(config_name))
        config_text = open(config_path).read()
        config = json.loads(config_text)
    except IOError:
        raise errors.ConfigIOError("Config file {} does not exist!".format(repr(config_path)))
    except ValueError:
        raise errors.ConfigParseError("Could not parse config file {}!".format(repr(config_path)))

    return config
