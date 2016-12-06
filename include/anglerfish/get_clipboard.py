#!/usr/bin/env python3
# -*- coding: utf-8 -*-


"""Determine OS and set copy() and paste() functions accordingly."""


import os
import sys
import subprocess
import logging as log

from shutil import which


def __osx_clipboard():
    def copy_osx(text):
        subprocess.Popen(["pbcopy"], stdin=subprocess.PIPE,
                         close_fds=True).communicate(text.encode("utf-8"))

    def paste_osx():
        os.environ["LANG"] = "en_US.utf-8"
        return str(subprocess.Popen(
            ["pbpaste"], stdout=subprocess.PIPE, close_fds=True
            ).communicate()[0].decode("utf-8"))

    return copy_osx, paste_osx


def __xclip_clipboard():
    def copy_xclip(text):
        subprocess.Popen(["xclip", "-selection", "clipboard"],
                         stdin=subprocess.PIPE, close_fds=True).communicate(
                         text.encode('utf-8'))
        if which("xsel"):
            subprocess.Popen(["xclip", "-selection", "primary"],
                             stdin=subprocess.PIPE, close_fds=True
                             ).communicate(text.encode('utf-8'))

    def paste_xclip():
        return subprocess.Popen(["xclip", "-selection",
                                 "primary" if which("xsel") else "clipboard",
                                 "-o"], stdout=subprocess.PIPE, close_fds=True
                                ).communicate()[0].decode("utf-8")

    return copy_xclip, paste_xclip


def __win32_clibboard():
    import win32clipboard
    import win32con

    def copy_win32(text):
        win32clipboard.OpenClipboard()
        win32clipboard.EmptyClipboard()
        win32clipboard.SetClipboardData(win32con.CF_UNICODETEXT, text)
        win32clipboard.CloseClipboard()

    def paste_win32():
        win32clipboard.OpenClipboard()
        text = win32clipboard.GetClipboardData(win32con.CF_UNICODETEXT)
        win32clipboard.CloseClipboard()
        return text

    return copy_win32, paste_win32


def __determine_clipboard():
    """Determine OS and set copy() and paste() functions accordingly."""
    if sys.platform.startswith("darwin"):
        return __osx_clipboard()
    if sys.platform.startswith("windows"):
        try:  # Determine which command/module is installed, if any.
            import win32clipboard  # lint:ok noqa
        except ImportError:
            log.error("Install Win32 API Python packages for Windows.")
            return None, None  # install Win32.
        else:
            return __win32_clibboard()
    if sys.platform.startswith("linux") and which("xclip"):
        return __xclip_clipboard()
    else:
        log.error("Install XClip and XSel Linux Packages at least.")
        return None, None  # install Qt or GTK or Tk or XClip.


def get_clipboard():
    """Crossplatform crossdesktop Clipboard."""
    log.debug("Querying Copy/Paste Clipboard functionality.")
    global clipboard_copy, clipboard_paste
    clipboard_copy, clipboard_paste = None, None
    clipboard_copy, clipboard_paste = __determine_clipboard()
    return clipboard_copy, clipboard_paste
