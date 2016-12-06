#!/usr/bin/env python3
# -*- coding: utf-8 -*-


"""Multithreading helper."""


from functools import wraps
from concurrent.futures import ThreadPoolExecutor


class _Threaded():

    def __init__(self, future, timeout):
        self._future, self._timeout = future, timeout

    def __getattr__(self, name):
        result = self._wait()
        return result.__getattribute__(name)

    def _wait(self):
        return self._future.result(self._timeout)


def _async(n, base_type, timeout=None):

    def decorator(f):
        if isinstance(n, int):
            pool = base_type(n)
        elif isinstance(n, base_type):
            pool = n
        else:
            raise TypeError("Invalid Type: {}".format(type(base_type)))

        @wraps(f)
        def wrapped(*args, **kwargs):
            return _Threaded(pool.submit(f, *args, **kwargs), timeout=timeout)
        return wrapped

    return decorator


def threads(n, timeout=None):
    return _async(n, ThreadPoolExecutor, timeout)
