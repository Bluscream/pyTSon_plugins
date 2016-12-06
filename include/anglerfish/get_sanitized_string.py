#!/usr/bin/env python3
# -*- coding: utf-8 -*-


"""Take and Return a string, but Sanitize all weird characters."""


import re


def get_sanitized_string(stringy, repla=""):
    """Take str sanitize non-printable weird characters,return clean str"""
    return re.sub(r"[^\x00-\x7F]+", repla, stringy, flags=re.IGNORECASE)
