#!/usr/bin/env python2
# -*- coding: utf-8 -*-

"""
Created on Tue Jul 18 13:17:36 2017

@author: vama
"""


from os import listdir, mkdir, getcwd, makedirs, chdir
from os.path import isfile, join, isdir, basename, normpath, dirname, curdir
from shutil import move
from nwchemwf import inputs
from orcawf import callorca, orcaloader
import json
import sys
import time

import sys
import signal
import functools
import time

inputs.create_list()
tot_inps = len(inputs.listofinputs)

dependson='conformers'



def early_dead(outfile, e, info, signum, stack):
    pname = inputs.get_name(e)
    print(" \n %s:Dead signal %s\n" % (pname, signum))

    info['lock'] = 'no'
    inputs.store_json(e,info)
    print("\n %s  exit NOW \n" % pname)
    sys.exit()


def run_orcajob(e, jobdetails, info):
    jobtype = 'orca'

#   info = inputs.load_json(e)
    smi = info["FILTERED"][0]["SMI"]

    pname = inputs.get_name_file(e)
    print("%s : SMILES: %s" % (pname, smi))

    #print len(info['conformers'])

    if jobtype in info:
        print "no"
        print ("%s: there are %s %s conformers" % (pname, jobtype, len(info[jobtype])))
        return -1


    calc_orca = []

    inpname = inputs.get_name_file(e) +'.inp'
    bestconf = inputs.get_bestconf(e, info)
    if None == bestconf:
        print("%s: there are not %s mopac conformers" % (pname))
        return False
    mols = {}
    mols['inchikey'] = info['inchikey']
    mols['coords'] = info["FILTERED"][0]['mopac'][bestconf]['coords']
    mols['charge'] = 0.0
    inputs.create_input(e,'config.json','.inp', mols)


    outfile = 'zindo.out'
#
# implement Signal catcher
#
    handler = functools.partial(early_dead, outfile, e, info)
    signal.signal(signal.SIGINT, handler)
    signal.signal(signal.SIGTERM, handler)

    callorca.run_orca(inpname)

    calc = {}
    if isfile(join(inputs.get_outpath(e),outfile)):
        try:
            print inputs.get_outpath(e)
            calc = orcaloader.load_calc_list(inputs.get_outpath(e))
            print calc

        except:
            info['lock']= 'ready'
            info["FILTERED"][0][jobtype]= 'fail'
            inputs.store_json(e,info)
            return True

    info["FILTERED"][0][jobtype] = calc
    # readey may be gone of there is jobtype
    info['lock']= 'ready'

    inputs.store_json(e,info)
    return True


def process(jobdetails):
    jobtype='orca'
##debug    print jobtype
    readys = 0
    tot_errors = 0
    while readys < tot_inps:
        print readys
        print tot_inps
        for e in range(tot_inps):

#vama pick one already checks locks
#           inputs.clean_db_for_job2(e, jobtype)

            status, info = inputs.pick_one(e, jobtype)
            pname = inputs.get_name_file(e)

            if status != -1 and inputs.prepare_outdir(e) :
                print(' %s : processing ' % pname)
                if not run_orcajob(e, jobdetails, info):
                    print ("%s: FAIL to  orca" % pname)
                    tot_errors = tot_errors + 1
                readys = readys + 1
            else:
                if 'lock' in info:
                    if info['lock'] == 'ready':
                        readys = readys + 1
                    else:
                        print("%s:no job " % pname)
                        time.sleep(1)

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

