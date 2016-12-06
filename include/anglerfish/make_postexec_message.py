#!/usr/bin/env python3
# -*- coding: utf-8 -*-


"""Simple Post-Execution Message with information about RAM and Time."""


import atexit
import logging as log
import os
import sys

from datetime import datetime

try:
    import resource
except ImportError:
    resource = None  # MS Window dont have resource


def make_post_exec_msg(start_time=None, comment=None):
    """Simple Post-Execution Message with information about RAM and Time."""
    use, al, msg = 0, 0, ""
    if sys.platform.startswith("windows"):
        msg = "No information about RAM usage available on non-Linux systems\n"
    elif sys.platform.startswith("linux"):
        use = int(resource.getrusage(resource.RUSAGE_SELF).ru_maxrss *
                  resource.getpagesize() / 1024 / 1024 if resource else 0)
        al = int(os.sysconf('SC_PAGE_SIZE') * os.sysconf('SC_PHYS_PAGES') /
                 1024 / 1024 if hasattr(os, "sysconf") else 0)
        msg += "Total Maximum RAM Memory used: {0} of {1}MegaBytes.\n".format(
            use, al)
        if start_time and datetime:
            msg += "Total Working Time: ~ {0}.\n".format(
                datetime.now() - start_time)
    if comment:
        msg += str(comment).strip()
    log.debug("Preparing Simple Post-Execution Messages.")
    atexit.register(log.info, msg)
    return msg
