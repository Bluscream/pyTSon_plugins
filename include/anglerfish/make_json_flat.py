#!/usr/bin/env python3
# -*- coding: utf-8 -*-


"""Make a JSON from Nested to Flat with an arbitrary delimiter."""


def make_json_flat(jsony, delimiter="__"):
    """Make a JSON from Nested to Flat with an arbitrary delimiter."""
    values = {}
    for item in jsony.keys():
        if isinstance(jsony[item], dict):
            get = make_json_flat(jsony[item], delimiter)
            for something in get.keys():
                values[item + delimiter + something] = get[something]
        else:
            values[item] = jsony[item]
    return values
