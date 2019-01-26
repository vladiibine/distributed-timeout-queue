import random
import time

import redis

from log_utils import log
from settings import TIMEOUT_WORK, PROCESS_WAIT_MIN, PROCESS_WAIT_MAX


def main():
    r = redis.Redis(host='redis')
    log("Worker starting")

    successful = 0
    total = 0

    for workload in pull_work(r):
        total += 1
        log(f"Worker starting to process {workload}")
        processed_work = process_workload(workload)
        success = acknowledge_completion(workload, processed_work, r)
        successful += 1 if success else 0

    log(f"Worker done. Successes: {successful}, total: {total} ({successful/total})")


def pull_work(r):
    workload = r.srandmember('todos')
    while workload is not None:
        workload = int(workload)
        # problem here: Maybe after moving the task, the cleaner
        # comes and moves if right back... we'll do at-least-once processing then
        did_move = r.smove("todos", "in_progress", workload)

        if did_move:
            r.setex(f"{workload}-lock", TIMEOUT_WORK, '')
            yield workload

        workload = r.srandmember('todos')


def process_workload(workload):
    # emulate work that might finish in-time, or slower
    wait_time = random.randint(PROCESS_WAIT_MIN, PROCESS_WAIT_MAX)
    log(f"Worker will sleep {wait_time} before processing {workload}")
    time.sleep(wait_time)
    return workload ** 3 - 1  # need to smartify this


def acknowledge_completion(workload, result, r):
    """
    :param workload:
    :param result:
    :param redis.Redis r:
    :return: success status
    """
    ttl = r.ttl(f"{workload}-lock")
    if ttl >= -1:
        pipeline = r.pipeline()
        pipeline.smove('in_progress', 'done', workload)

        # now... it can happen that the task is moved back
        # to "todos" by the cleaner at this point, so it will
        # be processed twice. We're going for at-least-once
        # processing (vs at most once processing)
        pipeline.delete(f"{workload}-lock")
        pipeline.execute()
        log(f"Executed workload: {workload} to get {result}")
        return True
    else:
        log(f"Sadly our work was rejected for workload {workload} even though we gor {result}")
        return False


if __name__ == '__main__':
    main()
