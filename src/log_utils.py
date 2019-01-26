import sys


def log(*args, **kwargs):
    print(*args, **kwargs)
    sys.stdout.flush()
