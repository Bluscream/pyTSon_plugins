#!/usr/bin/env python3
# -*- coding: utf-8 -*-


"""Test the Terminal Colors."""


def make_test_terminal_color():
    """Test the Terminal Colors."""
    print("Testing Terminal Colors...")
    r = g = b = 0
    result = ""
    for r in range(81):
        result += '\x1b[0;48;2;%s;%s;%sm ' % (r, g, b)
    result += "\n"
    r = 0
    for g in range(81):
        result += '\x1b[0;48;2;%s;%s;%sm ' % (r, g, b)
    result += "\n"
    g = 0
    for b in range(81):
        result += '\x1b[0;48;2;%s;%s;%sm ' % (r, g, b)
    result += '\x1b[0m \n'
    print(result)
    return result
