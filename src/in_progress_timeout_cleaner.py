import time
import sys

import redis

from log_utils import log
from queue_funcs import get_todos_len
from settings import TIMEOUT_WORK


def main():
    r = redis.Redis(host='redis')

    while True:
        time.sleep(TIMEOUT_WORK)
        log("Waking up cleaner")
        log(f'Still {get_todos_len(r)} tasks to execute')

        members = r.smembers('in_progress')
        log(f"Cleaner items in progress: {members}")
        if not members:
            continue

        for num in (int(m) for m in members):
            workload_lock_key = f'{num}-lock'
            workload_key = f'{num}'

            ttl = r.ttl(workload_lock_key)
            if int(ttl) == -2:
                log(f"!!!!~~~~Cleaner will reset {workload_key}")
                pipeline = r.pipeline()
                pipeline.delete(workload_lock_key)
                pipeline.smove('in_progress', 'todos', workload_key)
                pipeline.execute()


if __name__ == '__main__':
    main()
