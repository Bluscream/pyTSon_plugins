#!/usr/bin/env python3
# -*- coding: utf-8 -*-


"""Import a module from file path string."""


import logging as log
import importlib.util
import os


def path2import(pat, name=None):
    """Import a module from file path string.

    This is "as best as it can be" way to load a module from a file path string
    that I can find from the official Python Docs, for Python 3.5+."""
    module = None
    try:
        name = name if name else os.path.splitext(os.path.basename(pat))[0]
        spec = importlib.util.spec_from_file_location(name, pat)
        module = spec.loader.load_module()
    except Exception as error:
        log.warning("Failed to Load Module {0} from {1}.".format(name, pat))
        log.warning(error)
    else:
        log.debug("Loading Module {0} from file path {1}.".format(name, pat))
    finally:
        return module
