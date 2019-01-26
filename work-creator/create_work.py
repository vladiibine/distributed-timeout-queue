import redis


def main():
    r = redis.Redis(host='redis')

    # We'll just add 10k numbers, that workers will have to apply some math on
    for num in range(10):
        r.sadd('todos', num)


if __name__ == '__main__':
    main()
