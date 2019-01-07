# -*- coding: utf-8 -*-
"""
Spyder Editor

This is a temporary script file.
"""

import os
import json
from nwchemwf import callnwbg, loader, inputs

from re import findall


tot_inps = inputs.total_inputfiles()
inputs.create_list()


def main():
    for e in range(tot_inps):
       #inputs.clean_db(e)
       inputs.clean_db_ready(e)

if __name__ == "__main__":
    main()
# qmwf : quantum mechanics workflow for data science
# author: alvarovm at gihub

