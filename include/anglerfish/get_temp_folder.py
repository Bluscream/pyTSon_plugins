#!/usr/bin/env python3
# -*- coding: utf-8 -*-


"""Get a temp Sub-folder for this App only, cross-platform, return path."""


import logging as log
import os

from tempfile import gettempdir


def get_temp_folder(appname):
    """Get a temp Sub-folder for this App only, cross-platform, return path."""
    if appname and len(appname) and isinstance(appname, str):
        temp_path = os.path.join(gettempdir(), appname.strip().lower())
    log.debug("Temp folder for {0} is: {1}.".format(appname, temp_path))
    if not os.path.isdir(temp_path):
        log.debug("Creating new Temp folder: {0}.".format(temp_path))
        os.makedirs(temp_path)
    return temp_path
