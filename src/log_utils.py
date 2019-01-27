import os
import sys

from settings import ONLY_LOG_SUMMARY


def log(*args, force=False, **kwargs):
    if not force and ONLY_LOG_SUMMARY:
        return

    print(*args, **kwargs)
    sys.stdout.flush()


def name():
    # I don't expect the host or the PID of this to change, really...
    if not hasattr(name, '_cache'):
        name._cache = f"{os.environ.get('host', '?')}-{os.getpid()}"
    return name._cache
