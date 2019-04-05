from typing import Any, Callable, Iterator, List, Tuple

import cachetools

import utils

CACHE_ENABLED = True
CACHE_MAXSIZE = 2 ** 32

_caches = {}


def cached(maxsize: int = None, key: Callable = None, group: Any = None):
    maxsize = maxsize or CACHE_MAXSIZE
    key = key or _cachekey

    def outer(func):
        if CACHE_ENABLED:
            module = func.__module__
            name = func.__name__

            _caches[module + '.' + name] = cache = StatisticsCache(
                maxsize,
                group=group,
                module=module,
                name=name)

            @cachetools.cached(cache, key=key)
            def inner(*args, **kwargs):
                return func(*args, **kwargs)

            return inner
        else:
            return func

    return outer


class StatisticsCache(cachetools.RRCache):
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
        self.hit = self.miss = 0

    def get_stats(self) -> List[str]:
        hit = self.hit
        miss = self.miss
        total = (hit + miss) or 0.001
        size = len(self)

        return [f"Cache: {self.module + '.' + self.name}",
                f"Hit: {hit / total * 100 :.2f}%",
                f"Miss: {miss / total * 100:.2f}%",
                f"Capacity: {size / self.maxsize * 100:.2f}%",
                f"Size: {size}"]


def get_stats(**filters) -> str:
    table = []
    for _, v in _iter_caches(**filters):
        table.append(v.get_stats())
    return utils.justify_table(table)


def reset_stats(**filters) -> None:
    for _, v in _iter_caches(**filters):
        v.reset_stats()


def _iter_caches(group: Any = None,
                 module: str = None,
                 name: str = None) -> Iterator[Tuple[str, StatisticsCache]]:
    for k, v in _caches.items():
        if group is not None and v.group != group:
            continue
        if module is not None and v.module != module:
            continue
        if name is not None and v.name != name:
            continue
        yield k, v


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
