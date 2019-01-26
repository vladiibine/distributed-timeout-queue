import redis


def main():
    r = redis.Redis(host='redis')

    for workload in pull_work(r):
        processed_work = process_workload(workload)
        acknowledge_completion(workload, processed_work, r)


def pull_work(r):
    workload = r.srandmember('todos')
    while workload is not None:
        workload = int(workload)
        # problem here: Maybe after moving the task, the cleaner
        # comes and moves if right back... we'll do at-least-once processing then
        did_move = r.smove("todos", "in_progress", workload)

        if did_move:
            r.setex(f"{workload}-lock", 10, '')
            yield workload

        workload = r.srandmember('todos')


def process_workload(workload):
    return workload ** 3 - 1  # need to smartify this


def acknowledge_completion(workload, result, r):
    """
    :param workload:
    :param result:
    :param redis.Redis r:
    :return:
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
        print(f"Executed workload: {workload} to get {result}")
    else:
        print(f"Sadly our work was rejected for workload {workload} even though we gor {result}")


if __name__ == '__main__':
    main()
