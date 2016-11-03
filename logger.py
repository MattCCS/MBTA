
import datetime
import json
import sys
import time
import urllib.request
import xml.etree.ElementTree

from . import settings
from . import utils


def time_left(time_to_wait, time_before, time_after):
    return max(0, time_to_wait - max(0, time_after - time_before))


def form_prediction_json(prediction):
    return {
        'eta': int(prediction.get('epochTime')),
        'seconds': int(prediction.get('seconds')),
        'vehicle': prediction.get('vehicle'),
    }


def log_bus_data(config):
    url = config['url']
    delay = config['delay']

    log_path = settings.LOG_PATH / "{}.log".format(config['name'])

    with open(str(log_path), 'a') as log:
        while True:
            before = time.time()

            try:
                transit_html = urllib.request.urlopen(url).read()
                transit_xml = xml.etree.ElementTree.fromstring(transit_html)
            except Exception as err:
                utils.stderr("Error: {}".format(err))

            try:
                predictions = transit_xml[0][0].getchildren()
                predictions = [form_prediction_json(pred) for pred in predictions]
            except IndexError:
                predictions = []

            all_data = {
                'now': int(datetime.datetime.now().strftime("%s")),
                'predictions': predictions,
            }

            log.write("{}\n".format(json.dumps(all_data)))
            log.flush()

            after = time.time()
            time.sleep(time_left(delay, before, after))


def main():
    args = utils.parse_args()
    config = utils.load_config(args.config)
    log_bus_data(config)


if __name__ == '__main__':
    utils.stdout("Starting...")

    try:
        main()
    except KeyboardInterrupt:
        utils.stdout("Closed.")
