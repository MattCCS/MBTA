
import datetime

from . import settings

import twilio
from twilio.rest import TwilioRestClient


SID = "ACe05942b8265752c56cda142903d0efce"
TOKEN = "6dac0e75da6a7cff323ac4482a8fd91e"
NUMBER = "+16035132500"
MATT = "+16032752718"

CLIENT = TwilioRestClient(SID, TOKEN)


def get_after(after, from_):
    return [r for r in CLIENT.messages.list(after=after, from_=from_) if r.date_sent > after]

def get_today(from_):
    return get_after(datetime.datetime.now().date(), from_)


def send(to, msg, from_=NUMBER):
    return CLIENT.messages.create(to=to, from_=from_, body=msg)

