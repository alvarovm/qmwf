# -*- coding: utf-8 -*-
#
# Copyright (c) 2016, the cclib development team
#
# This file is part of cclib (http://cclib.github.io) and is distributed under
# the terms of the BSD 3-Clause License.

import sys

if 'PyQt4' in list(sys.modules.keys()):
    from .qt4progress import Qt4Progress

from .textprogress import TextProgress

# qmwf : quantum mechanics workflow for data science
# author: alvarovm at gihub

