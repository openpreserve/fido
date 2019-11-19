#!/usr/bin/env python
# -*- coding: utf-8 -*-

from time import sleep

from fido.fido import PerfTimer


def test_perf_timer():
    timer = PerfTimer()
    sleep(3.6)
    duration = timer.duration()
    assert duration > 0
