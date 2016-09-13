
import argparse
import datetime
import re
import sys
import time
import urllib

import data

# assert sys.version_info >= (3, 5)


parser = argparse.ArgumentParser()
parser.add_argument("-v", "--verbose", type=int, default=0)
args = parser.parse_args()


SECONDS_PATTERN = r'''seconds="(\d+)"'''
PAUSE = 5
VERBOSE = args.verbose


def mmss(seconds):
    (minutes, seconds) = divmod(seconds, 60)
    return "{}:{:02}".format(minutes, seconds)


def yield_for_url(url):
    while True:
        before = time.time()

        try:
            xml = str(urllib.urlopen(url).read())
        except urllib.error as e:
            print("Error: {}".format(e))

        now = datetime.datetime.now()
        times = re.findall(SECONDS_PATTERN, xml)

        # if VERBOSE == 0:
        yield data.DataPoint(int(now.strftime("%s")), map(int, times))
        # elif VERBOSE == 1:
        #     yield data.DataPoint(now.strftime("%c"), ', '.join(map(mmss, map(int, times))))

        after = time.time()
        remaining = max(0, PAUSE - max(0, after - before))

        time.sleep(remaining)
