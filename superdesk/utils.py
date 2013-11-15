
import string
import random


def get_random_string(length=12):
    chars = string.ascii_letters + string.digits
    return ''.join([random.choice(chars) for i in range(length)])
