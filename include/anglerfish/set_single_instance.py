#!/usr/bin/env python3
# -*- coding: utf-8 -*-


"""Set process name and cpu priority,return socket.socket or None."""


import logging as log
import socket
import sys


def set_single_instance(name, port=8888):
    """Set process name and cpu priority,return socket.socket or None."""
    try:  # Single instance app ~crossplatform, uses udp socket.
        log.info("Creating Abstract UDP Socket Lock for Single Instance.")
        __lock = socket.socket(
            socket.AF_UNIX if sys.platform.startswith("linux")
            else socket.AF_INET, socket.SOCK_STREAM)
        __lock.bind(
            "\0_{name}__lock".format(name=str(name).lower().strip())
            if sys.platform.startswith("linux") else ("127.0.0.1", port))
    except (socket.error, OSError, Exception) as e:
        __lock = None
        log.critical("Another instance of App is already running!, Exiting!.")
        log.exception(e)
        sys.exit()
        exit()
    else:
        log.info("Socket Lock for Single Instance: {}.".format(__lock))
    finally:
        return __lock
