#!/usr/bin/env python2
# -*- coding: utf-8 -*-

"""
Created on Tue Jul 18 13:17:36 2017

@author: vama
"""


from os import listdir, mkdir, getcwd, makedirs, chdir
from os.path import isfile, join, isdir, basename, normpath, dirname, curdir
from shutil import move, copyfile
from nwchemwf import callnwbg, loader, inputs
from external_libs import bgqtools
import json

tot_inps = inputs.total_inputfiles()
inputs.create_list()

#print tot_inps

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
    smi = info["smiles"]
    pname = inputs.get_name(e)
    print("%s : SMILES: %s" % (pname, smi))

    bestconf = inputs.get_bestconf(e)
    if None == bestconf:
        print("%s: there are not %s mopac conformers" % (pname))
        return False
    mols = {}
    mols['inchikey'] = info['inchikey']
    mols['coords'] = info['mopac'][bestconf]['coords']
    mols['charge'] = 0.0
    inputs.create_input(e,'config_nw.json','.nw', mols)

    inpname = inputs.get_name_file(e) +'.nw'

    copyfile(inpname, 'nwchem.nw')

    print job
    callnwbg.run_nwchem('nwchem', job)
    outfile = 'nwchem.out'
    calc_mop = []

    if isfile(outfile):
            calc = loader.load_calc_list(inputs.get_outpath(e), 'nwchem.out')
            calc_mop.append(calc)

    info['nwchem'] = calc_mop

    info['lock']= 'ready'

    inputs.store_json(e,info)

    return True

def process(job):
    jobtype = 'nwchem'
    for e in range(tot_inps):
        inputs.clean_db_for_job2(e, jobtype)
        status = inputs.pick_one(e, jobtype)
        if status != -1:

            pname = inputs.prepare_outdir(e)

            print(' processing : %s' % pname)

            if not run_nwchemjob_best(e, job):
                print ("%s: FAIL to runmopac" % pname)

def main():
    #read_arc(mp_name)
    #print (properties['totale'])
    partsize, partition, job_id = bgqtools.get_cobalt_info()

    jobdetails = {}
    jobdetails['bgq'] = True
    jobdetails['modes'] = 8
    jobdetails['thres'] = 1
    jobdetails['block_size']  = partsize
    jobdetails['block']  = partition
    process(jobdetails)




if __name__ == "__main__":
       main()

# qmwf : quantum mechanics workflow for data science
# author: alvarovm at gihub

