#!/usr/bin/env python3
# -*- coding: utf-8 -*-


"""Add to autostart or launcher icon on the Desktop."""


import logging as log
import os
import sys


def set_desktop_launcher(app, desktop_file_content, autostart=False):
    """Add to autostart or launcher icon on the Desktop."""
    if not sys.platform.startswith("linux"):
        return  # .desktop files are Linux only AFAIK.
    # Auto-Start file below.
    config_dir = os.path.join(os.path.expanduser("~"), ".config", "autostart")
    os.makedirs(config_dir, exist_ok=True)
    autostart_file = os.path.join(config_dir, app + ".desktop")
    if os.path.isdir(config_dir) and not os.path.isfile(autostart_file):
        if autostart:
            log.info("Writing Auto-Start Executable file: " + autostart_file)
            with open(autostart_file, "w", encoding="utf-8") as start_file:
                start_file.write(desktop_file_content)
        if os.path.isfile(autostart_file):
            os.chmod(autostart_file, 0o776)
    # Desktop Launcher file below.
    apps_dir = os.path.join(os.path.expanduser("~"),  # paths are XDG.
                            ".local", "share", "applications")
    os.makedirs(apps_dir, exist_ok=True)
    desktop_file = os.path.join(apps_dir, app + ".desktop")
    if os.path.isdir(apps_dir) and not os.path.isfile(desktop_file):
        log.info("Writing Desktop Launcher Executable file: " + desktop_file)
        with open(desktop_file, "w", encoding="utf-8") as desktop_file_obj:
            desktop_file_obj.write(desktop_file_content)
    if os.path.isfile(desktop_file):
        os.chmod(desktop_file, 0o776)
    return desktop_file
