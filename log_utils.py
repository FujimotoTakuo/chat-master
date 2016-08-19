#!/usr/bin/env python
# -*- coding: utf-8 -*-

import time
from datetime import datetime as dt, timedelta

def log(message):
    log_file = open('log.txt', 'w')
    log_file.write(str(dt.now()) + ' : ' + str(message))
    print(str(message))
    log_file.close()
