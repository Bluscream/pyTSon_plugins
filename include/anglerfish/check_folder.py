#!/usr/bin/env python3
# -*- coding: utf-8 -*-


"""Check working folder,from argument,for everything that can go wrong."""


import logging as log
import os

from shutil import disk_usage


def check_folder(folder_to_check=os.path.expanduser("~"), check_space=True):
    """Check working folder,from argument,for everything that can go wrong."""
    folder_to_check = os.path.abspath(folder_to_check)  # More Safe on WinOS
    log.debug("Checking the Working Folder: '{0}'".format(folder_to_check))
    if not isinstance(folder_to_check, str):  # What if folder is not a string.
        log.critical("Folder {0} is not String type!.".format(folder_to_check))
        return False
    elif not os.path.isdir(folder_to_check):  # What if folder is not a folder.
        log.critical("Folder {0} does not exist!.".format(folder_to_check))
        return False
    elif not os.access(folder_to_check, os.R_OK):  # What if not Readable.
        log.critical("Folder {0} not Readable !.".format(folder_to_check))
        return False
    elif not os.access(folder_to_check, os.W_OK):  # What if not Writable.
        log.critical("Folder {0} Not Writable !.".format(folder_to_check))
        return False
    elif disk_usage and os.path.exists(folder_to_check) and check_space:
        hdd = int(disk_usage(folder_to_check).free / 1024 / 1024 / 1024)
        if hdd:  # > 1 Gb
            log.info("Folder Total Free Space: ~{0} GigaBytes.".format(hdd))
            return True
        else:  # < 1 Gb
            log.critical("Total Free Space is < 1 GigaByte; Epic Fail!.")
            return False
    return False
