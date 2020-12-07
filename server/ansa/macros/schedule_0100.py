from datetime import time
from .schedule import schedule


def callback(item, **kwargs):
    return schedule(item, time(1, 0))


name = "Schedule publishing at 1:00"
label = name
access_type = "backend"
action_type = "direct"
