
import datetime

import mbta
from Gmail import gmail


DICT_DAYSTRING_TO_DAY = dict(zip('MTWRFSU', range(7)))  # datetime.weekday()

CONFIGS = {}


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
        gmail.send_email(
            self.phone,
            "You should leave in {time} minutes for {line}!".format(
                line=self.line, time=td.seconds // 60),
            "The bus should arrive at {prediction}, and it will take you {travel} minutes to walk there.".format(
                prediction=data.next_predicted().strftime("%X")[:-3], travel=self.travel_minutes)
            )

    def in_range(self, dt):
        return (dt.weekday() in self.days)

    def check(self, data_before, data_after):
        print("checking...")

        if not data_before or not data_after:
            return

        # print(data_before.next_delta(), data_after.next_delta())

        now = datetime.datetime.now()
        if not self.in_range(now):
            return

        for time in self.time_deltas:
            delta = time + self.travel_delta
            # print()
            # print(time, self.travel_delta, delta)
            print(data_before.next_delta(), delta, data_after.next_delta())
            if data_before.next_delta() >= delta > data_after.next_delta():
                # "You should leave in {time} minutes"
                # "It will take {self.travel_delta} minutes to walk there"
                self.email(time, data_after)

    def __repr__(self):
        return str(self.__dict__)


def load_configs():
    global CONFIGS

    with open("configs.csv") as configs:
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
