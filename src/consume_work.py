import multiprocessing
import random
import time
import os

import redis

from log_utils import log
from settings import TIMEOUT_WORK, PROCESS_WAIT_MIN, PROCESS_WAIT_MAX, NUM_WORKERS, ITEMS_TO_PROCESS


def main(*args, **kwargs):
    r = redis.Redis(host='redis')
    log(f"Worker {os.getpid()} starting")

    successful = 0
    total = 0

    for workload in pull_work(r):
        total += 1
        log(f"Worker {os.getpid()} starting to process {workload}")
        processed_work = process_workload(workload)
        success = acknowledge_completion(workload, processed_work, r)
        successful += 1 if success else 0

    # in real-life, a worker never "finishes". The for loop would be run
    # in a while-true loop actually
    log(f">>>>>Worker {os.getpid()} done. Successes: {successful}, total: {total} ({successful/(total or 1)})")


def pull_work(r):
    workload = r.srandmember('todos')
    while workload is not None:
        workload = int(workload)
        # problem here: Maybe after moving the task, the cleaner
        # comes and moves if right back... we'll do at-least-once processing then
        did_move = r.smove("todos", "in_progress", workload)

        if did_move:
            pipeline = r.pipeline()
            pipeline.set(f"{workload}-lock", '')
            pipeline.pexpire(f"{workload}-lock", int(TIMEOUT_WORK * 1000))
            pipeline.execute()
            yield workload

        workload = r.srandmember('todos')


def process_workload(workload):
    # emulate work that might finish in-time, or slower
    wait_time = PROCESS_WAIT_MIN + random.random() * (PROCESS_WAIT_MAX - PROCESS_WAIT_MIN)
    log(f"Worker {os.getpid()} will sleep {wait_time} before processing {workload}")
    time.sleep(wait_time)
    return workload ** 3 - 1


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
        log(f"Worker {os.getpid()} executed workload: {workload} to get {result}")
        return True
    else:
        log(f"Worker {os.getpid()} - :( sadly our work was rejected for workload {workload} even though we gor {result}")
        return False


if __name__ == '__main__':
    pool = multiprocessing.Pool(processes=NUM_WORKERS)
    pool.map(main, [()] * NUM_WORKERS)
