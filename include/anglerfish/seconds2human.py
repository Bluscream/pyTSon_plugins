#!/usr/bin/env python3
# -*- coding: utf-8 -*-


"""Calculate time, with precision from seconds to days."""


def seconds2human(time_on_seconds=0, do_year=True):
    """Calculate time, with precision from seconds to days."""
    minutes, seconds = divmod(int(abs(time_on_seconds)), 60)
    hours, minutes = divmod(minutes, 60)
    days, hours = divmod(hours, 24)
    human_time_string = ""
    years = int(int(days) / 365)
    if days and years and do_year and years > 1:
            human_time_string += "{0} Years ".format(years)
            days = days - (365 * years)
    if days:
        human_time_string += "%02d Days " % days
    if hours:
        human_time_string += "%02d Hours " % hours
    if minutes:
        human_time_string += "%02d Minutes " % minutes
    human_time_string += "%02d Seconds" % seconds
    return human_time_string


def timedelta2human(time_delta, do_year=True):  # Just a shortcut :)
    """Convert a TimeDelta object to human string representation."""
    return seconds2human(time_delta.total_seconds(), do_year=do_year)
