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

    info['lock'] = 'no'
    try:
        calc = loader.load_calc_list(inputs.get_outpath(e), outfile)
        info["FILTERED"][0]['nwchem'] = calc
    except:
        # it fails but just move on
        print("%s: ed failed to parse a nwchemout named %s" % (pname, outfile))
        print("%s: ed failed to parse a nwchemout thispath %s" % (pname, inputs.get_outpath(e)))
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

def run_nwchemjob_best(e, job, info):
#   info = inputs.load_json(e)
    smi = info["FILTERED"][0]["SMI"]
    pname = inputs.get_name_file(e)
    print("%s : SMILES: %s" % (pname, smi))

    need_restart = False

    outfile = 'nwchem.out'
    print outfile


#    if isfile(outfile):
#        prevcalc = loader.load_calc_list(inputs.get_outpath(e), outfile, 'opt')
#        optdone = prevcalc['optdone']
#        if prevcalc['optdone'] == True:
#            inputs.put_lock(e,'ready')
#            return False
#        elif  prevcalc['optdone'] == False:
#            need_restart = True
#            rename_w_num(outfile)
#        else:
#            print ('%s: WARNING did something did not go further' % pname)
#            return False

    try:
        if 'optdone' in info["FILTERED"][0]['nwchem']:
            if  info["FILTERED"][0]['nwchem']['optdone'] == True:
                inputs.put_lock(e,'ready', info)
                return True
#           else:
            elif info["FILTERED"][0]['nwchem']['optdone'] == False:
                need_restart = True
            elif info["FILTERED"][0]['nwchem']['optdone'] == None:
                need_restart = False

            if isfile(outfile):
                 rename_w_num(outfile)
#            elif  info['nwchem']['optdone'] == False:
#                need_restart = True
#                if isfile(outfile):
#                    rename_w_num(outfile)
#            else:
#                print ('%s: WARNING did something did not go further' % pname)
#                return False
    except:
        print ("%s: no nwchem  optdone info" % pname )


    mols = {}
    inpname = inputs.get_name_file(e) +'.nw'
    if need_restart:
        if isfile(inpname):
            rename_w_num(inpname)
        #we could restar with mols from prevcalc
        mols['inchikey'] = info['inchikey']
        mols['charge'] = 0.0
        mols['coords'] = info["FILTERED"][0]['nwchem']['coords']

        inputs.create_input(e,'config_nwres.json','.nw', mols)

    else :
        bestconf = inputs.get_bestconf(e, info)

        if None == bestconf:
            print("%s: there are not best mopac conformers" % (pname))
            return False
    #        mols = {}
        mols['inchikey'] = info['inchikey']
        mols['coords'] = info["FILTERED"][0]['mopac'][bestconf]['coords']
        mols['charge'] = 0.0
        inputs.create_input(e,'config_nw.json','.nw', mols)

    copyfile(inpname, 'nwchem.nw')

    outfile = 'nwchem.out'
    print outfile
#
# implement Signal catcher
#
    handler = functools.partial(early_dead, outfile, e, info)
    signal.signal(signal.SIGINT, handler)
    signal.signal(signal.SIGTERM, handler)

# Do calculation
    callnwbg.run_nwchem_sub('nwchem', job)

##debug    print ("callnwbg My PID is: %s \n" % getpid())
##debug    time.sleep(4000)
#   calc_mop = []

    calc = {}
    if isfile(join(inputs.get_outpath(e),outfile)):
        try:
            calc = loader.load_calc_list(inputs.get_outpath(e), outfile)
        except:
            # it fails but just move on
            info['lock']= 'ready'
            info["FILTERED"][0]['nwchem']= 'fail'
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

#vama pick one already checks locks
#           inputs.clean_db_for_job2(e, jobtype)

            status, info = inputs.pick_one(e, jobtype)
            pname = inputs.get_name_file(e)

            if status != -1 and inputs.prepare_outdir(e) :
                print(' %s : processing ' % pname)
                if not run_nwchemjob_best(e, job, info):
                    print ("%s: FAIL to  nwchem" % pname)
                    tot_errors = tot_errors + 1
                readys = readys + 1
            else:
                if 'lock' in info:
                    if info['lock'] == 'ready':
                        readys = readys + 1
                    else:
                        print("%s:no job " % pname)
                        time.sleep(1)
#maybe the script should crash if it cannot write to disk

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

