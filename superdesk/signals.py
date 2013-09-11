
import blinker

def connect(signal, subscriber):
    blinker.signal(signal).connect(subscriber)

def send(signal, *args):
    blinker.signal(signal).send(*args)
