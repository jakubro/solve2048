from typing import Any, Callable

import cachetools

CACHE_ENABLED = True
CACHE_MAXSIZE = 256

_caches = {}


def cached(maxsize: int = None, key: Callable = None, group: Any = None):
    maxsize = CACHE_MAXSIZE

    def outer(func):
        if CACHE_ENABLED:
            module = func.__module__
            name = func.__name__

            _caches[module + '.' + name] = cache = StatisticsCache(
                maxsize,
                group=group,
                module=module,
                name=name)

            @cachetools.cached(cache, key=key or _cachekey)
            def inner(*args, **kwargs):
                return func(*args, **kwargs)

            return inner
        else:
            return func

    return outer


class StatisticsCache(cachetools.LRUCache):
    def __init__(self,
                 *args,
                 group: Any = None,
                 module: str = None,
                 name: str = None,
                 **kwargs):
        super().__init__(*args, **kwargs)
        self.group = group
        self.module = module
        self.name = name
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

    def reset_stats(self) -> None:
        self.hit = 0
        self.miss = 0


def get_stats(group: Any = None,
              module: str = None,
              name: str = None) -> str:
    rv = ""
    for k, v in _caches.items():
        if group is not None and v.group != group:
            continue
        if module is not None and v.module != module:
            continue
        if name is not None and v.name != name:
            continue

        hit = v.hit
        miss = v.miss
        total = (hit + miss) or 0.001

        rv += (f"Cache: {k}:\t"
               f"Hit: {hit / total * 100 :.2f}%\t"
               f"Miss: {miss / total * 100:.2f}%\n")
    return rv


def reset_stats(group: Any = None,
                module: str = None,
                name: str = None) -> None:
    for v in _caches.values():
        if group is not None and v.group != group:
            continue
        if module is not None and v.module != module:
            continue
        if name is not None and v.name != name:
            continue

        v.reset_stats()


def _cachekey(*args, **kwargs):
    args = tuple(_as_tuple(a) for a in args)
    kwargs = tuple((k, _as_tuple(v)) for k, v in kwargs.items())
    return hash(tuple((args, kwargs)))


def _as_tuple(obj):
    if isinstance(obj, dict):
        return tuple(obj.items())

    try:
        iter(obj)
    except TypeError:
        return tuple([obj])
    else:
        return tuple(obj)
