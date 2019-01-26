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
    return get_redis_set_len(r, 'todos')


def get_done_len(r):
    return get_redis_set_len(r, 'done')


def get_in_progress_len(r):
    return get_redis_set_len(r, 'in_progress')
