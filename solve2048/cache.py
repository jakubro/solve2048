from typing import Callable

import cachetools

CACHE_ENABLED = True


def cachekey(*args, **kwargs):
    args = [tuple(a.items()) if isinstance(a, dict) else a
            for a in args]
    kwargs = {k: (tuple(v.items()) if isinstance(v, dict) else v)
              for k, v in kwargs.items()}
    return hash(tuple((tuple(args), tuple(kwargs.items()))))


class StatCache(cachetools.RRCache):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.hit = 0
        self.miss = 0

    def __getitem__(self, *args, **kwargs):
        try:
            rv = super().__getitem__(*args, **kwargs)
        except KeyError as e:
            self.miss += 1
            raise e
        else:
            self.hit += 1
            return rv


def cached(maxsize: int = 2 ** 512, key: Callable = None):
    def outer(func):
        if CACHE_ENABLED:
            cache = StatCache(maxsize)

            @cachetools.cached(cache, key=key or cachekey)
            def inner(*args, **kwargs):
                return func(*args, **kwargs)

            inner._cache = cache
            return inner
        else:
            return func

    return outer
