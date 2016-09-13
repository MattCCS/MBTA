
import datetime


class DataPoint(object):

    def __init__(self, timestamp, predicted_delta_seconds):
        self.timestamp = datetime.datetime.fromtimestamp(timestamp / 1e3)
        self.predicted_delta_seconds = [datetime.timedelta(seconds=t) for t in sorted(predicted_delta_seconds)]

    def datetime(self):
        return self.timestamp

    def time(self):
        return self.timestamp.time()

    def next_delta(self):
        return self.predicted_delta_seconds[0]

    def next_predicted(self):
        return (self.timestamp + self.next_delta()).time()
