from gevent import monkey
monkey.patch_all()
import gevent

import collections
import functools
import time
import datetime

import redis

from log_utils import log
from queue_funcs import get_todos_len, get_in_progress_len, get_done_len, get_redis_set_members, \
    get_redis_list_members
from request_utils import random_delay
from settings import CLEANER_SLEEPS_FOR, TODOS_QUEUE_NANE, IN_PROGRESS_QUEUE_NAME, DONE_QUEUE_NAME, \
    ITEMS_TO_PROCESS


def main():
    r = redis.Redis(host='redis')

    # Keep track of "how many tasks are in progress"
    conclusion_logger = ConclusionLogger(r)

    while True:
        time.sleep(CLEANER_SLEEPS_FOR)
        log("Waking up cleaner")
        conclusion_logger.update_todos_length()

        todos_len = get_todos_len(r)
        log(f'Still {todos_len} tasks to execute')

        # TODO - instead of retrieving all the keys, maybe use SSCAN
        in_progress_items = random_delay(
            lambda: r.smembers('in_progress'), delay_multiplier=0.01)

        # Some logging in case the workload appears to be done, for the
        # current batch at least
        log(f"Cleaner items in progress: {in_progress_items}")
        conclusion_logger.log_conclusions()

        if not in_progress_items:
            continue

        in_progress_lock_keys = [f'{int(num)}-lock' for num in in_progress_items]

        in_progress_responses = random_delay(lambda: r.mget(in_progress_lock_keys))

        num_keys_to_reset = len([e for e in in_progress_responses if e is None])

        # log(f"in_progress keys to query: {in_progress_lock_keys}", force=True)
        # log(f"in_progress_responses {in_progress_responses}", force=True)
        for idx, (resp, lock_key, key) in enumerate(zip(in_progress_responses, in_progress_lock_keys, in_progress_items)):
            if resp is None:
                # TODO - we can probably use something like gevent here. This takes REALLY long!
                log(f"!!!!~~~~Cleaner will reset {key} ({idx+1}/{num_keys_to_reset})", force=True)
                pipeline = random_delay(lambda: r.pipeline())
                random_delay(lambda: pipeline.delete(lock_key))
                random_delay(lambda: pipeline.smove(IN_PROGRESS_QUEUE_NAME, TODOS_QUEUE_NANE, key))
                random_delay(lambda: pipeline.execute())


class ConclusionLogger:
    def __init__(self, r):
        self.todos_len_tracker = collections.deque([], 5)
        self.start_date = datetime.datetime.now()
        self.r = r
        self.already_logged = False

    def log_conclusions(self):
        force_log = functools.partial(log, force=True)

        if all(i == 0 for i in self.todos_len_tracker) and not self.already_logged:

            self.already_logged = True
            end_date = (datetime.datetime.now() - datetime.timedelta(seconds=5 * CLEANER_SLEEPS_FOR))
            time_interval = end_date - self.start_date

            force_log("Cleaner: works appears to be done...for now",)
            force_log(f"in progress: {get_in_progress_len(self.r)}")
            force_log(f"done: {get_done_len(self.r)}", )
            force_log(f"todos: {get_todos_len(self.r)}", )
            force_log(f"-------------------------------------", )
            force_log(f"todos: {get_redis_list_members(self.r, TODOS_QUEUE_NANE)}", )
            force_log(f"in_progres: {get_redis_set_members(self.r, IN_PROGRESS_QUEUE_NAME)}")
            # force_log(f"done: {list(sorted((get_redis_set_members(self.r, DONE_QUEUE_NAME))))[:100]}")
            done_elems = list(sorted((get_redis_set_members(self.r, DONE_QUEUE_NAME))))
            should_have_done_elems = list(range(ITEMS_TO_PROCESS))

            if done_elems != should_have_done_elems:
                force_log(f"len(done_elens): {len(done_elems)}")
                force_log(f"len(should_have_done): {len(should_have_done_elems)}")
                force_log("!!!The done list differs from expectations!!!")
                # force_log(f"missing: {set(should_have_done_elems) - set(done_elems)}")
                # force_log(f"extra: {set(done_elems) - set(should_have_done_elems)}")
                counter = collections.Counter(done_elems)
                # force_log(f"{counter.most_common()}")
                for elem in counter:
                    if counter[elem] > 1:
                        force_log(f'item {elem} was present {counter[elem]} times')

            # force_log(f"done contains numbers 0..{ITEMS_TO_PROCESS - 1}: {list(sorted((get_redis_set_members(self.r, DONE_QUEUE_NAME)))) == list(range(ITEMS_TO_PROCESS))}")
            force_log(f"Items/second processed: {ITEMS_TO_PROCESS/time_interval.total_seconds()}")

        elif not self.already_logged:
            force_log(f"Cleaner, last todos lengths: {self.todos_len_tracker}. "
                      f"Work considered done if only 0s appear")

    def update_todos_length(self):
        self.todos_len_tracker.append(get_todos_len(self.r))


if __name__ == '__main__':
    main()
