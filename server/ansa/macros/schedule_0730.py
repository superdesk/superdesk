from datetime import time
from .schedule import schedule


def callback(item, **kwargs):
    return schedule(item, time(7, 30))


name = "Schedule publishing at 7:30"
label = name
access_type = "backend"
action_type = "direct"
