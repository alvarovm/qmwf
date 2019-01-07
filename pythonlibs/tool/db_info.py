#!/usr/bin/env python2
# -*- coding: utf-8 -*-

"""
Created on Tue Jul 18 13:17:36 2017

@author: vama
"""


from os import listdir, mkdir, getcwd, makedirs, chdir
##debugfrom os import getpid
from os.path import isfile, join, isdir, basename, normpath, dirname, curdir
from shutil import move, copyfile
from nwchemwf import callnwbg, loader, inputs
import json
from external_libs import bgqtools

import sys
import signal
import functools
import time


inputs.create_list()
tot_inps = len(inputs.listofinputs)

SIGNALS = {
    signal.SIGINT: 'SIGINT',
    signal.SIGTERM: 'SIGTERM',
}

def early_dead(outfile, e, info, signum, stack):
    pname = inputs.get_name(e)
    print(" \n %s:Dead signal %s\n" % (pname, signum))

    info['lock']='no'
    try:
        calc = loader.load_calc_list(inputs.get_outpath(e), outfile)
        info["FILTERED"][0]['nwchem'] = calc
    except:
        # it fails but just move on
        print("%s:  ed failed to parse a nwchemout" % pname)
        info["FILTERED"][0]['nwchem']= 'fail'
    finally:
        inputs.store_json(e,info)
        print("\n %s  exit NOW \n" % pname)
        sys.exit()


def confgen_analysis(e, job):
    info = inputs.load_json(e)

    if 'lock'in info:
        if info['lock'] == 'yes':
            lock = 1
        else:
            lock = 0
    else:
        lock = 0

    try:
        if 'conformers' in info["FILTERED"][0]:
            return -1, lock
        else:
            return 0, lock
    except:
        return 0, lock

def mopac_analysis(e, job):
    info = inputs.load_json(e)

    if info['lock'] == 'yes':
        lock = 1
    else:
        lock = 0

    try:
        if 'mopac' in info["FILTERED"][0]:
            return -1, lock
        else:
            return 0, lock
    except:
        return 0, lock

def nwchemout_analysis(e, job):
    info = inputs.load_json(e)

    if info['lock'] == 'yes':
        lock = 1
    else:
        lock = 0

    try:
        if 'optdone' in info["FILTERED"][0]['nwchem']:
            if info["FILTERED"][0]['nwchem']['optdone'] == True:
                return -1, lock
            else:
                return -2, lock
        else:
            return 0, lock
    except:
        return 0, lock

def process(job):
    jobtype = 'nwchem'
##debug    print jobtype
    locks = 0
    opts = 0
    for e in range(tot_inps):
        pname = inputs.get_name_file(e)
        status , lock = nwchemout_analysis(e, jobtype)
        #status , lock = mopac_analysis(e, jobtype)
        #status , lock = confgen_analysis(e, jobtype)
        locks = locks + lock
        if status == -1:
            opts = opts + 1
    print(" total of structures %d " % tot_inps)
    print(" total of locks %d " %  locks)
    print(" total of opts %d " %  opts)
    print(" total of opts left %d " %  (tot_inps - opts))


def main(jobdetails):
    #read_arc(mp_name)
    #print (properties['totale'])
    #partsize, partition, job_id = bgqtools.get_cobalt_info()

#   jobdetails = {}
#   jobdetails['bgq'] = True
#   jobdetails['modes'] = 8
#   jobdetails['thres'] = 1
#   jobdetails['block_size']  = partsize
#   jobdetails['block']  = partition

    for k, v in jobdetails.items():
	print('keyword argument2: {} = {}'.format(k, v))
    process(jobdetails)
    return True


if __name__ == "__main__":
#        print sys.argv[1:]
#       	kk=dict( arg.split('=') for arg in sys.argv[1:])
#	print kk
#	main(kk)
    print sys.argv[1:]
    kk=dict( arg.split('=') for arg in sys.argv[1:])
    print kk

    status = main(kk)
    if not status:
        for k, v in kk.items():
	    print('keyword argument: {} = {}'.format(k, v))
 	print("check args")

# qmwf : quantum mechanics workflow for data science
# author: alvarovm at gihub

