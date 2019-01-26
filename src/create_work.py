import redis

from settings import ITEMS_TO_PROCESS, TODOS_QUEUE_NANE


def main():
    r = redis.Redis(host='redis')

    # We'll just add 10k numbers, that workers will have to apply some math on
    for num in range(ITEMS_TO_PROCESS):
        r.sadd(TODOS_QUEUE_NANE, num)


if __name__ == '__main__':
    main()
