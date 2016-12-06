#!/usr/bin/env python3
# -*- coding: utf-8 -*-


"""Notification message with information, based on D-Bus, with Fallbacks."""


import logging as log

from shutil import which
from subprocess import call

try:
    import dbus
except ImportError:
    dbus = None

try:
    import pynotify
except ImportError:
    pynotify = None


def make_notification(title, message="", name="", icon="", timeout=3000):
    """Notification message with information,based on D-Bus,with Fallbacks."""
    if dbus:  # Theorically the standard universal way.
        log.debug("Sending Notification message via D-Bus API.")
        return dbus.Interface(dbus.SessionBus().get_object(
            "org.freedesktop.Notifications", "/org/freedesktop/Notifications"),
            "org.freedesktop.Notifications").Notify(
                name, 0, icon, title, message, [], [], timeout)
    elif pynotify:  # The non-standard non-universal way.
        log.debug("Sending Notification message via PyNotify API.")
        pynotify.init(name.lower() if name else title.lower())
        return pynotify.Notification(title, message).show()
    elif which("notify-send"):   # The non-standard non-universal sucky ways.
        log.debug("Sending Notification message via notify-send command.")
        comand = (which("notify-send"), "--app-name=" + name,
                  "--expire-time=" + str(timeout), title, message)
        return not bool(call(comand, timeout=timeout // 1000 + 1))
    elif which("kdialog"):
        log.debug("Sending Notification message via KDialog command.")
        comand = (which("kdialog"), "--name=" + name, "--title=" + title,
                  "--icon=" + icon, "--caption=" + name, "--passivepopup",
                  title + message, str(timeout // 1000))
        return not bool(call(comand, timeout=timeout // 1000 + 1))
    elif which("zenity"):
        log.debug("Sending Notification message via Zenity command.")
        comand = (which("zenity"), "--name=" + name, "--title=" + title,
                  "--notification", "--timeout=" + str(timeout // 1000),
                  "--text=" + title + message)
        return not bool(call(comand, timeout=timeout // 1000 + 1))
    elif which("xmessage"):  # This one is Ugly, but I hope you never get here.
        log.warning("Sending Notification message via XMessage command.")
        comand = (which("xmessage"), "-center", title + message)
        return not bool(call(comand, timeout=timeout // 1000 + 1))
    else:  # Windows and Mac dont have API for that, complain to them.
        log.warning("Sending Notifications not supported by this OS.")
        return False
