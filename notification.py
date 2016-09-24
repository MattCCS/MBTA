
import datetime

from . import mbta
from . import settings
from . import twilio_tools

# from Gmail import gmail


DICT_DAYSTRING_TO_DAY = dict(zip('MTWRFSU', range(7)))  # datetime.weekday()

CONFIGS = {}

NOTIFICATION_FORM = """\
Leave in {time} minutes for {line}!

{linecap} should arrive at {prediction}, leaving {travel} minutes to walk there."""


def pairs(iterator):
    prev = None
    for elem in iterator:
        yield (prev, elem)
        prev = elem


def to_time(timestring):
    return datetime.datetime.strptime("{:0>8}".format(timestring), "%I:%M %p").time()


class NotificationConfig(object):

    def __init__(self, name, phone, days, between, times, travel_minutes, line, url):
        self.name = name
        self.phone = phone
        self.days = set(DICT_DAYSTRING_TO_DAY[day] for day in days)
        (self.start, self.end) = map(to_time, between.split('-'))
        self.time_deltas = [datetime.timedelta(minutes=int(t)) for t in times.split(' ')]
        self.travel_minutes = travel_minutes
        self.travel_delta = datetime.timedelta(minutes=int(travel_minutes))
        self.line = line
        self.url = url

    def email(self, td, data):
        print(td)

        time_ = td.seconds // 60
        print(data.next_predicted())
        prediction = data.next_predicted().strftime("%-I:%M %p")

        twilio_tools.send(
            self.phone,
            NOTIFICATION_FORM.format(
                time=time_,
                line=self.line,
                linecap=self.line.capitalize(),
                prediction=prediction,
                travel=self.travel_minutes,
            )
        )

    def in_range(self, dt):
        in_day_set = dt.weekday() in self.days
        in_time_range = (self.start <= dt.time() <= self.end)
        # return (in_day_set and in_time_range)
        # return (in_day_set)
        return True

    def check(self, data_before, data_after):
        print("checking...")

        if not data_before or not data_after:
            return

        now = datetime.datetime.now()
        if not self.in_range(now):
            return

        for time in self.time_deltas:
            delta = time + self.travel_delta
            print(data_before.next_delta(), delta, data_after.next_delta())
            if data_before.next_delta() >= delta > data_after.next_delta():
                self.email(time, data_after)

    def __repr__(self):
        return str(self.__dict__)


def load_configs():
    global CONFIGS

    with open(str(settings.CONFIGS_PATH)) as configs:
        configs.readline()
        for line in configs:
            try:
                config = NotificationConfig(*line.split(','))
                CONFIGS[config.name] = config
            except Exception as e:
                print(e, line)

    print(CONFIGS)


def main():
    load_configs()

    matt = CONFIGS["Matt"]
    for (before, after) in pairs(mbta.yield_for_url(matt.url)):
        matt.check(before, after)


if __name__ == '__main__':
    main()
