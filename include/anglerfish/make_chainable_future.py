#!/usr/bin/env python3
# -*- coding: utf-8 -*-


"""Make a Chainable concurrent.futures.Future that has a .then() api."""


import sys
import weakref

from concurrent.futures import Future


class ChainableFuture(Future):

    """Make a Chainable concurrent.futures.Future that has a .then() api."""

    @property
    def _chained_future_log(self):
        """Chained Future Log."""
        prop_name = '_chained_futured_log_list'
        log = getattr(self, prop_name, None)
        if log is None:
            log = weakref.WeakSet()
            setattr(self, prop_name, log)
        return log

    def _chain_to_another_future(self, base_future):
        """Chains a Future instance directly to another Future instance."""
        msg = "Circular chain error.Future {} is already in resolved chain {}."
        if base_future in self._chained_future_log:
            raise Exception(msg.format(base_future,
                                       set(self._chained_future_log)))
        else:
            self._chained_future_log.add(base_future)

        def _done_handler(base_future):
            """Converts return of previous Future to results of new Future."""
            if not base_future.done():  # Never True. Avoid infinite timeout.
                self.cancel()
                return
            if base_future.cancelled():
                self.cancel()
                return
            try:
                result = base_future.result()
                if isinstance(result, Future):
                    self._chain_to_another_future(result)
                else:
                    self.set_result(result)
                return
            except BaseException:
                ex, trace_back = sys.exc_info()[1:]
                self.set_exception_info(ex, trace_back)
                return
        base_future.add_done_callback(_done_handler)

    def then(self, on_success=None, on_fail=None):
        """Chainable concurrent.futures.Future.then() JS-like

        - on_success: Optional,Callable to run when this Future success Ok.
        - on_fail: Optional,Callable to run when this Future fails.
        - Return: Future chained to current Future.
        """
        new_future = self.__class__()

        def _done_handler(base_future):
            """Converts result of previous Future to result of new Future."""
            if not base_future.done():  # Never True. Avoid infinite timeout.
                new_future.cancel()
                return
            if base_future.cancelled():
                new_future.cancel()
                return
            try:
                result = base_future.result()
                if on_success:
                    result = on_success(result)
                if isinstance(result, Future):  # Defer resolution new_future
                    new_future._chain_to_another_future(result)
                else:
                    new_future.set_result(result)
                    return
            except BaseException:
                ex, trace_back = sys.exc_info()[1:]
                if not on_fail:
                    new_future.set_exception_info(ex, trace_back)
                    return
                else:
                    try:
                        result = on_fail(ex)
                        if isinstance(result, BaseException):
                            raise result
                        else:
                            new_future.set_result(result)
                        return
                    except BaseException:
                        ex, trace_back = sys.exc_info()[1:]
                        new_future.set_exception_info(ex, trace_back)
                        return
        self.add_done_callback(_done_handler)
        return new_future
