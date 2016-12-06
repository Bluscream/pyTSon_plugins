#!/usr/bin/env python3
# -*- coding: utf-8 -*-


"""Get and return a free unused port."""


import socket

import logging as log


def get_free_port(port_range=(8000, 9000)):
    """Get and return a free unused port."""
    sockety = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sockety.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    for port_number in range(int(port_range[0]), int(port_range[1])):
        try:
            sockety.bind(("127.0.0.1", port_number))
        except (socket.error, Exception):
            pass
        else:
            sockety.close()
            del sockety
            log.debug("Found free unused port number: {0}".format(port_number))
            return port_number
