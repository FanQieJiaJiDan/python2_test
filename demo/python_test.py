#!/usr/bin/python
# -*- coding: UTF-8 -*-
import datetime
import logging
import traceback
from demo_1 import WORKER_PATH
logger = logging.getLogger('mylogger')


class PrintText:
    def __init__(self):
        pass

    def start(self):
        try:
            now_datetime = (datetime.datetime.now())
            num_c = 1 + '5'

            # import pydevd
            # pydevd.settrace('192.168.11.29', port=12321, stdoutToServer=True, stderrToServer=True)
            logger.info(now_datetime)

        except Exception as e:
            logger.error(e)
            logger.error(traceback.format_exc())

# PrintText().start()
