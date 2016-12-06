#!/usr/bin/env python3
# -*- coding: utf-8 -*-


"""Set or Reset CLI Window Titlebar Title. Linux only?."""


def set_terminal_title(titlez=""):
    """Set or Reset CLI Window Titlebar Title. Linux only?."""
    if titlez and len(titlez.strip()) and isinstance(titlez, str):
        print(r"\x1B]0; {0} \x07".format(titlez.strip()))
        return titlez
    else:
        print(r"\x1B]0;\x07")
