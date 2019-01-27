# work is considered timed out after this many seconds. The task gets
# put back in the TODOS list, from the IN_PROGRESS set
TIMEOUT_WORK = 1  # seconds

# How much time does the cleaner wait until cleaning up timed-out tasks
CLEANER_SLEEPS_FOR = 20  # seconds

# How many items we should process
ITEMS_TO_PROCESS = 10000

# A worker waits at least this amount of time (seconds) before processing the work
PROCESS_WAIT_MIN = 0  # seconds
# A worker waits at most this many seconds before processing the owrk
PROCESS_WAIT_MAX = 0.22  # seconds
# When there's no work in the queue, a worker will sleep for this many seconds before
# waking up to poll again
PROCESS_WAIT_IDLE = 1  # seconds

# How much time would we wait for the network requests to go through
RANDOM_DELAY_MIN = 0  # seconds
RANDOM_DELAY_MAX = 0.2  # seconds

# Number of processes processing work
NUM_WORKERS = 40

# This value will be used for the lock-keys... we don't really need any value, but
# since it's reused, it's good to save it here
LOCK_VALUE = b''


# The names of the 3 queues we're using
TODOS_QUEUE_NANE = 'todos'
IN_PROGRESS_QUEUE_NAME = 'in_progress'
DONE_QUEUE_NAME = 'done'

# If this is False, output from all the workers and the cleaner will be shown
# When True, we'll only show a summary report, once the work seems to be all done
ONLY_LOG_SUMMARY = True
