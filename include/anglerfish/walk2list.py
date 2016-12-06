#!/usr/bin/env python3
# -*- coding: utf-8 -*-


"""Perform full walk of where, gather full path of all files."""


import logging as log
import os


def walk2list(where, target, omit, links=False, tuply=True):
    """Perform full walk of where, gather full path of all files."""
    log.debug("Scan {},searching {},ignoring {}.".format(where, target, omit))
    listy = [os.path.abspath(os.path.join(r, f))
             for r, d, fs in os.walk(where, followlinks=links)
             for f in fs if not f.startswith('.') and
             not f.endswith(omit) and
             f.endswith(target)]  # only target files,no hidden files
    return tuple(listy) if tuply else listy
