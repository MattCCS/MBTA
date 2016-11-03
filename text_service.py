
import datetime
import json
import subprocess
import sys

from . import data
from . import settings
from . import twilio_tools
from . import utils


DICT_DAYSTRING_TO_DAY = dict(zip('MTWRFSU', range(7)))  # datetime.weekday()

CONFIGS = {}

NOTIFICATION_FORM = """\
Leave {when} for {line}!

{linecap} should arrive at {prediction}, leaving {travel} minutes to get there."""



def pairs(iterator):
    prev = None
    for elem in iterator:
        yield (prev, elem)
        prev = elem


def to_time(timestring):
    return datetime.datetime.strptime("{:0>8}".format(timestring), "%I:%M %p").time()


def yield_datapoints(log_name):
    log_path = str(settings.LOG_PATH / "{}.log".format(log_name))
    log = subprocess.Popen(['tail', '-n', '2', '-f', log_path], stdout=subprocess.PIPE)

    for line in log.stdout:
        line = line.decode('utf-8')
        yield data.DataPoint(json.loads(line))


def us_eastern_now():
    return datetime.datetime.now() + datetime.timedelta(hours=4)


class NotificationConfig(object):

    def __init__(self, name, phone, days, between, times, travel_minutes, line, url):
        self._enabled = True
        self.name = name
        self.phone = phone
        self.days = set(DICT_DAYSTRING_TO_DAY[day] for day in days)
        (self.start, self.end) = [to_time(t) for t in between.split('-')]
        self.time_deltas = [datetime.timedelta(minutes=int(t)) for t in times]
        self.travel_minutes = travel_minutes
        self.travel_delta = datetime.timedelta(minutes=int(travel_minutes))
        self.line = line
        self.url = url

    @staticmethod
    def load(config_dict):
        return NotificationConfig(
            config_dict['name'],
            config_dict['phone'],
            config_dict['days'],
            config_dict['hours'],
            config_dict['reminders'],
            config_dict['lead'],
            config_dict['description'],
            config_dict['url'],
        )

    def text(self, td, data):
        print(td)

        time_ = td.seconds // 60
        print(data.next_predicted())
        prediction = data.next_predicted().strftime("%-I:%M %p")

        if time_:
            when = "in {time} minutes".format(time=time_)
        else:
            when = "NOW"

        twilio_tools.send(
            self.phone,
            NOTIFICATION_FORM.format(
                when=when,
                line=self.line,
                linecap=self.line.capitalize(),
                prediction=prediction,
                travel=self.travel_minutes,
            )
        )

    def in_range(self, dt):
        in_day_set = dt.weekday() in self.days
        in_time_range = (self.start <= dt.time() <= self.end)
        if not in_time_range:
            utils.stdout("Not in time range!")
        elif not in_day_set:
            utils.stdout("Not in day range!")
        return (in_day_set and in_time_range)
        # return (in_day_set)
        # return True

    def check(self, data_before, data_after):
        print("\nChecking...")

        if not self._enabled:
            print("Disabled.")
            return

        if not data_before or not data_after:
            print("Missing data!")
            return

        now = datetime.datetime.now()
        if not self.in_range(now):
            return

        for time in self.time_deltas:
            delta = time + self.travel_delta
            print(data_before.next_delta(), delta, data_after.next_delta())
            if data_before.next_delta() >= delta > data_after.next_delta():
                try:
                    self.text(time, data_after)
                except Exception as err:
                    print(err)

    def handle_incoming(self, incoming):
        inp = incoming.body.strip().lower()
        if inp in set(['ok', 'done', 'quit', 'disable', 'thanks', 'thx']):
            self._enabled = False
            twilio_tools.send(
                self.phone,
                "Ok!  Disabling service until tomorrow!\n\n(Or until you send 'GO')",
            )
        elif inp in set(['begin', 'run', 'go', 'enable']):
            self._enabled = True
            twilio_tools.send(
                self.phone,
                "Enabling service.",
            )
        elif inp == '<3':
            twilio_tools.send(self.phone, "<3!")
        else:
            twilio_tools.send(self.phone, "You can send me 'GO' and 'OK'.  Or '<3'.")

    def __repr__(self):
        return str(self.__dict__)


class TextService(object):

    def __init__(self, config_name):
        self._most_recent = us_eastern_now()
        self.config = utils.load_config(config_name)
        self.notification = NotificationConfig.load(self.config)

    def run(self):
        for (before, after) in pairs(yield_datapoints(self.config['name'])):

            try:
                incoming = twilio_tools.get_after(self._most_recent, self.config['phone'])[::-1]
                if incoming:
                    print("Got incoming: {}".format([r.body for r in incoming]))
                    for inc in incoming:
                        self.notification.handle_incoming(inc)
                    self._most_recent = us_eastern_now()   # TODO: this needs to be fixed eventually
            except ConnectionResetError:
                print("[Twilio update failed]")
            except Exception as err:
                print(err)

            self.notification.check(before, after)


def main():
    args = utils.parse_args()

    service = TextService(args.config)
    service.run()


if __name__ == '__main__':
    utils.stdout("Starting...")

    try:
        main()
    except KeyboardInterrupt:
        utils.stdout("Closed.")

