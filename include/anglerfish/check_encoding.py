#!/usr/bin/env python3
# -*- coding: utf-8 -*-


"""Debug and Log Encodings and Check for root/administrator,return Bool."""


import logging as log
import os
import sys

from getpass import getuser
from platform import platform, python_version


def check_encoding(check_root=True):
    """Debug and Log Encodings and Check for root/administrator,return Bool."""
    log.debug("Python {0} on {1}.".format(python_version(), platform()))
    log.debug("STDIN Encoding: {0}.".format(sys.stdin.encoding))
    log.debug("STDERR Encoding: {0}.".format(sys.stderr.encoding))
    log.debug("STDOUT Encoding:{}".format(getattr(sys.stdout, "encoding", "")))
    log.debug("Default Encoding: {0}.".format(sys.getdefaultencoding()))
    log.debug("FileSystem Encoding: {0}.".format(sys.getfilesystemencoding()))
    log.debug("PYTHONIOENCODING Encoding: {0}.".format(
        os.environ.get("PYTHONIOENCODING", None)))
    os.environ["PYTHONIOENCODING"] = "utf-8"
    if sys.platform.startswith(("linux", "darwin")) and check_root:  # root
        if not os.geteuid():
            log.warning("Runing as root is not Recommended !.")
            return False
    elif sys.platform.startswith("windows") and check_root:  # administrator
        if getuser().lower().startswith("admin"):
            log.warning("Runing as Administrator is not Recommended !.")
            return False
    return True
