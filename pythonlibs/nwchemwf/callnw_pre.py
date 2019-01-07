#!/usr/bin/env python2
# -*- coding: utf-8 -*-

"""
Created on Tue Jul 18 13:17:36 2017

@author: vama
"""


from os import listdir, mkdir, getcwd, makedirs, chdir
from os.path import isfile, join, isdir, basename, normpath, dirname, curdir
from shutil import move, copyfile
from nwchemwf import callnw, inputs , loader
import loader
import json

tot_inps = inputs.total_inputfiles()
inputs.create_list()

#print tot_inps

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

def run_nwchemjob_best(e):
    info = inputs.load_json(e)
    smi = info["smiles"]
    pname = inputs.get_name(e)
    print("%s : SMILES: %s" % (pname, smi))

    need_restart = False

    outfile = 'nwchem.out'


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
        if 'optdone' in info['nwchem']:
            if info['nwchem']['optdone'] == True:
                inputs.put_lock(e,'ready')
                return True
            elif  info['nwchem']['optdone'] == False:
                need_restart = True
                if isfile(outfile):
                    rename_w_num(outfile)
            else:
                print ('%s: WARNING did something did not go further' % pname)
                return False
    except:
        print ("%s no nwcheminfo" % pname )


    mols = {}
    inpname = inputs.get_name_file(e) +'.nw'
    if need_restart:
        if isfile(inpname):
            rename_w_num(inpname)
        #we could restar with mols from prevcalc
        mols['inchikey'] = info['inchikey']
        mols['charge'] = 0.0
        mols['coords'] = info['nwchem']['coords']

        inputs.create_input(e,'config_nwres.json','.nw', mols)

    else:

        bestconf = inputs.get_bestconf(e)
        if None == bestconf:
            print("%s: there are not %s mopac conformers" % (pname))
            return False
    #        mols = {}
        mols['inchikey'] = info['inchikey']
        mols['coords'] = info['mopac'][bestconf]['coords']
        mols['charge'] = 0.0
        inputs.create_input(e,'config_nw.json','.nw', mols)

    copyfile(inpname, 'nwchem.nw')

    callnw.run_nwchem('nwchem')

#    calc_mop = []
    calc = {}
    if isfile(outfile):
        try:
            calc = loader.load_calc_list(inputs.get_outpath(e), 'nwchem.out')
        except:
            # it fails but just move on
            info['lock']= 'ready'
            info['nwchem']= 'fail'
            inputs.store_json(e,info)

            return True

#            calc_mop.append(calc)
    #info['nwchem'] = calc_mop



    if calc['optdone'] == True:
#        info['nwchem'] = calc_mop
        info['lock']= 'ready'
    else:
        info['lock']= 'no'

    info['nwchem'] = calc
    inputs.store_json(e,info)

    return True


def main():

    jobtype = 'nwchem'
    readys = 0
    while readys < tot_inps:
        for e in range(tot_inps):

            inputs.clean_db_for_job2(e, jobtype)
            status = inputs.pick_one(e, jobtype)
            if status != -1:

                pname = inputs.prepare_outdir(e)

                print(' processing : %s' % pname)

                if not run_nwchemjob_best(e):
                    print ("%s: FAIL to runmopac" % pname)

            else:
                if inputs.get_lock(e) == 'ready':
                    readys = readys + 1
                else:
                    print("no job no job no job ")



if __name__ == "__main__":
       main()

# qmwf : quantum mechanics workflow for data science
# author: alvarovm at gihub

