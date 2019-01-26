import sys

from settings import ONLY_LOG_SUMMARY


def log(*args, force=False, **kwargs):
    if not force and ONLY_LOG_SUMMARY:
        return

    print(*args, **kwargs)
    sys.stdout.flush()
