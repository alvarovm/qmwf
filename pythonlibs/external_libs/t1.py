#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Wed Nov  8 16:35:28 2017

@author: vama
"""

from filelock import FileLock
import json
from os import getcwd
from os.path import isfile, join
import time

filename='hola.json'
full = join(getcwd(),filename)
if isfile(full):
    print 'yeassssssss'
with FileLock(filename,getcwd(),600):
    with open(full, 'r') as f:
        info = json.load(f)
    time.sleep(50)
print info# qmwf : quantum mechanics workflow for data science
# author: alvarovm at gihub

