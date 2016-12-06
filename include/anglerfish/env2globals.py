#!/usr/bin/env python3
# -*- coding: utf-8 -*-


"""Add ENV environtment variables to python globals dict."""


import os
import logging as log


def env2globals(pattern="PY_"):
    """Add ENV environtment variables to python globals dict."""
    log.debug("Adding environtment variables that match {0} to globals".format(
              pattern))
    try:
        for var in [_ for _ in os.environ.items() if _[0].startswith(pattern)]:
            globals().update({var[0]: var[1]})  # tuple to dict
    except Exception as e:
        log.warning(e)
        return False
    else:
        return True
