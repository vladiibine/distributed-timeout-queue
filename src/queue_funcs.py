from settings import TODOS_QUEUE_NANE, DONE_QUEUE_NAME, IN_PROGRESS_QUEUE_NAME


def get_redis_set_len(r, set_name):
    """
    :param redis.Redis r:
    :return: the length or -1 -> if unknown
    """
    try:
        return int(r.scard(set_name))
    except:
        return -1


def get_todos_len(r):
    return get_redis_set_len(r, TODOS_QUEUE_NANE)


def get_done_len(r):
    return get_redis_set_len(r, DONE_QUEUE_NAME)


def get_in_progress_len(r):
    return get_redis_set_len(r, IN_PROGRESS_QUEUE_NAME)


def get_redis_list_members(r, set_name, begin=0, end=-1):
    """

    :param redis.Redis r:
    :param set_name:
    :return:
    """
    try:
        return [int(i) for i in r.lrange(set_name, begin, end)]
    except:
        return []


def get_redis_set_members(r, set_name):
    """

    :param redis.Redis r:
    :param set_name:
    :return:
    """
    try:
        return [int(i) for i in r.smembers(set_name)]
    except:
        return []
