import time
import random

from settings import RANDOM_DELAY_MIN, RANDOM_DELAY_MAX


def random_delay(func, *args, delay_multiplier=1, **kwargs):
    """

    :param func:
    :param args:
    :param float delay_multiplier: need to use a delay multiplier, because the cleaner
        does a for through all the keys. The time adds up for 100k keys :P
    :param kwargs:
    :return:
    """
    wait_time = RANDOM_DELAY_MIN + random.random() * (RANDOM_DELAY_MAX - RANDOM_DELAY_MIN)
    wait_time *= delay_multiplier
    time.sleep(wait_time)

    return func(*args, **kwargs)
