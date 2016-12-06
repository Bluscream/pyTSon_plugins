#!/usr/bin/env python3
# -*- coding: utf-8 -*-


"""Log Exceptions but pretty printing with more info, return string."""


import logging as log
import sys
import traceback


def log_exception():
    """Log Exceptions but pretty printing with more info, return string."""
    unfriendly_names = {"<module>": "Unnamed Anonymous Module Function",
                        "<stdin>": "System Standard Input Function"}
    line_tpl = "    |___ {key} = {val}  # Type: {t}, Size: {s}Bytes, ID: {i}\n"
    body_tpl = """
    ################################ D E B U G ###############################
    Listing all Local objects by context frame, ordered by innermost last:
    {body}
    Thats all we know about the error, check the LOG file and StdOut.
    ############################### D E B U G #############################"""
    tb, body_txt, whole_txt = sys.exc_info()[2], "", ""
    while 1:
        if not tb.tb_next:
            break
        tb = tb.tb_next
    stack = []
    f = tb.tb_frame
    while f:
        stack.append(f)
        f = f.f_back
    stack.reverse()
    traceback.print_exc()
    for frame in stack:
        if frame.f_code.co_name in unfriendly_names.keys():
            fun = unfriendly_names[frame.f_code.co_name]
        else:
            fun = "Function {0}()".format(frame.f_code.co_name)
        body_txt += "\nThe {nm} from file {fl} at line {ln} failed!.".format(
            nm=fun, fl=frame.f_code.co_filename, ln=frame.f_lineno)
        body_txt += "\n    {}\n    |\n".format(fun)
        for key, value in frame.f_locals.items():
            whole_txt += line_tpl.format(key=key, val=repr(value)[:50],
                                         t=str(type(value))[:25],
                                         s=sys.getsizeof(key), i=id(value))
    result = body_tpl.format(body=body_txt + whole_txt)
    log.debug(result)
    return result
