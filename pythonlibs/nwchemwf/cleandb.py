# -*- coding: utf-8 -*-
"""
Spyder Editor

This is a temporary script file.
"""

import os
import json
from nwchemwf import inputs

from re import findall


tot_inps = inputs.total_inputfiles()
inputs.create_list()

jobtype='mopac'




def main():

    for e in range(tot_inps):
        inputs.clean_db(e)

if __name__ == "__main__":
       main()

# qmwf : quantum mechanics workflow for data science
# author: alvarovm at gihub

