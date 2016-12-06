#!/usr/bin/env python3
# -*- coding: utf-8 -*-


"""Set process name and cpu priority."""


import logging as log
import os

from ctypes import byref, cdll, create_string_buffer


def set_process_name(name):
    """Set process name and cpu priority."""
    try:
        os.nice(19)  # smooth cpu priority
        libc = cdll.LoadLibrary("libc.so.6")  # set process name
        buff = create_string_buffer(len(name.lower().strip()) + 1)
        buff.value = bytes(name.lower().strip().encode("utf-8"))
        libc.prctl(15, byref(buff), 0, 0, 0)
    except Exception as e:
        log.warning(e)
        return False  # this may fail on windows and its normal, so be silent.
    else:
        log.debug("Process Name set to: {0}.".format(name))
        return True
