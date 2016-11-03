
import collections
import datetime


class DataPoint(object):

    def __init__(self, data_json):
        self.timestamp = datetime.datetime.fromtimestamp(data_json['now'])
        self.predictions = sorted(data_json['predictions'], key=lambda d: int(d['seconds']))

    def has_times(self):
        return bool(self.predictions)

    def datetime(self):
        return self.timestamp

    def time(self):
        return self.timestamp.time()

    def next_delta(self):
        return datetime.timedelta(seconds=self.predictions[0]['seconds'])

    def next_predicted(self):
        return (self.timestamp + self.next_delta()).time()

    def __bool__(self):
        return self.has_times()
