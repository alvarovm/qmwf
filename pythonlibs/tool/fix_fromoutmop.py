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


def rename_w_num(src):
    count = 0
    dest = src+'_'+str(count)
    while 1:
        if not isfile(dest):
            move(src,dest)
            break
        else:
            count = count + 1
            dest = src+'_'+str(count)

def run_nwchemjob(e):


    info = inputs.load_json(e)
    smi = info["smiles"]

    pname = inputs.get_name(e)
    print("%s : SMILES: %s" % (pname, smi))

    if 'mopac' in info:
        print("%s: there are %s mopac conformers" % (pname, len(info['mopac'])))
    else:
        print("%s: there are not %s mopac conformers" % (pname))
        return False

    if 'nwchem' in info:
        print("%s: there are %s nwchem conformers" % (pname, len(info['nwchem'])))
        return True

    calc_mop = []
    for cc in range(len(info['conformers'])):
        mols = {}
        mols['inchikey'] = info['inchikey']
        mols['coords'] = info['mopac'][cc]['coords']
        mols['charge'] = 0.0
        #print mols
        print ("%s: Processing CONF %s" % (pname, cc))
        fname='_CONF_'+ str(cc)

        inputs.create_input(e,'config_nw.json',fname+'.nw', mols)

        inpname = inputs.get_name_file(e) + fname + '.nw'

        copyfile(inpname, 'nwchem')

        callnw.run_nwchem('nwchem')
        outfile = 'nwchem.out'
        if isfile(outfile):
            calc = loader.load_calc_list(inputs.get_outpath(e), 'nwchem.out')
            calc_mop.append(calc)


        info['nwchem'] = calc_mop

        inputs.store_json(e,info)

def run_nwchemjob_best(e, job):
    info = inputs.load_json(e)
    smi = info["FILTERED"][0]["SMI"]
    pname = inputs.get_name(e)
    print("%s : SMILES: %s" % (pname, smi))

    need_restart = False

    outfile = join(inputs.get_outpath(e),'nwchem.out')
    print outfile

    calc = {}
    if isfile(outfile):
        try:
            calc = loader.load_calc_list(inputs.get_outpath(e), 'nwchem.out')
        except:
            # it fails but just move on
            info["FILTERED"][0]['nwchem'] = 'fail'
            info['lock']= 'ready'
            inputs.store_json(e,info)
            return True
#           calc_mop.append(calc)
#   info['nwchem'] = calc_mop
    else:
        info['lock']= 'no'
        inputs.store_json(e,info)
        return True

    if calc['optdone'] == True:
        info['lock']= 'ready'
    else:
        info['lock']= 'no'

    info["FILTERED"][0]['nwchem'] = calc
    inputs.store_json(e,info)

    return True

def process(job):
    jobtype = 'nwchem'
##debug    print jobtype
    readys = 0
    tot_errors = 0
    while readys < tot_inps:
        print readys
        print tot_inps
        for e in range(tot_inps):
            pname = inputs.get_name(e)

            print(' %s : processing ' % pname)

            if not run_nwchemjob_best(e, job):
                 print ("%s: FAIL to runmopac" % pname)
                 tot_errors = tot_errors + 1
            readys = readys + 1

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

