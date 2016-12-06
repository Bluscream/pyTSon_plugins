#!/usr/bin/env python3
# -*- coding: utf-8 -*-


"""Set or Get a ZIP comment on its Metadata, return Bool."""


import logging as log

from zipfile import ZipFile


def set_zip_comment(zip_path, comment=""):
    """Set a ZIP comment."""
    try:
        with ZipFile(str(zip_path), 'a') as myzip:
            myzip.comment = bytes(str(comment).strip().encode("utf-8"))
    except Exception as error:
        log.warning("Failed to set comment to ZIP file: {0}.".format(zip_path))
        log.debug(error)
        return False
    else:
        log.debug("Setting comment to ZIP file: {0}.".format(zip_path))
        return True


def get_zip_comment(zip_path):
    """Get a ZIP comment."""
    try:
        log.debug("Getting comment from ZIP file: {0}.".format(zip_path))
        with ZipFile(str(zip_path), 'r') as myzip:
            return str(myzip.comment.decode("utf-8")).strip()
    except Exception as error:
        log.warning("Failed to get comment from ZIP: {0}.".format(zip_path))
        log.debug(error)
        return ""
