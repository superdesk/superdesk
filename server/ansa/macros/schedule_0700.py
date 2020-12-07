from datetime import time
from .schedule import schedule


def callback(item, **kwargs):
    return schedule(item, time(7, 0))


name = "Schedule publishing at 7:00"
label = name
access_type = "backend"
action_type = "direct"
