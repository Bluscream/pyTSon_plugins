#!/usr/bin/env python3
# -*- coding: utf-8 -*-


"""Install handler attach post-mortem pdb console on an exception."""


import logging as log
import sys
import traceback


def pdb_on_exception(debugger="pdb", limit=100):
    """Install handler attach post-mortem pdb console on an exception."""
    log.debug("Installing an automatic Debugger upon Exceptions...")

    def pdb_excepthook(exc_type, exc_val, exc_tb):
        traceback.print_tb(exc_tb, limit=limit)
        __import__(str(debugger).strip().lower()).post_mortem(exc_tb)

    sys.excepthook = pdb_excepthook


def ipdb_on_exception(debugger="ipdb", limit=100):
    """pdb_on_exception but using iPDB instead."""
    return pdb_on_exception("ipdb", limit=limit)


# ptpdb_on_exception = lambda: pdb_on_exception("ptpdb")
# See https://github.com/jonathanslenders/ptpdb/issues/14
