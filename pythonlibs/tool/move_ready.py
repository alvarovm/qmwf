# -*- coding: utf-8 -*-
"""
Spyder Editor

This is a temporary script file.
"""

import os
import openbabel
import json
import sys
from nwchemwf import inputs
import shutil
import callconfgen

from shutil import move

from re import findall


inputs.create_list()
tot_inps = len(inputs.listofinputs)




def process(jobdetails):
    jobtype='conformers'
    thisdir = os.getcwd()
    ready_files= os.path.join(thisdir,'readys')
    print tot_inps
    for e in range(tot_inps):
        if inputs.listofinputs[e].lock =='ready':
            print inputs.get_name_file(e)
            try:
               move(inputs.listofinputs[e].fullpath,ready_files)
            except:
                print "cannot move"
##caca            status = inputs.pick_one(e, jobtype)
##caca            pname = inputs.get_name_file(e)
##caca
##caca            if status != -1 and inputs.prepare_outdir(e) :
##caca                print(' %s : processing ' % pname)
##caca                if not run_confgen(e, jobdetails)
##caca                    print ("%s: FAIL to  %s" % (pname, jobtype))
##caca                    tot_errors = tot_errors + 1
##caca                readys = readys + 1
##caca            else:
##caca                if inputs.get_lock(e) == 'ready':
##caca                    readys = readys + 1
##caca                else:
##caca                    print("%s:no job " % pname)
##caca                    time.sleep(1)

##caca    for e in range(tot_inps):
##caca        status = inputs.pick_one(e,jobtype)
##caca#        if status == -1: break
##caca        if status != -1 :
##caca            pname = inputs.prepare_outdir(e)
##caca
##caca            print('%s: START processing ' % pname)
##caca            run_confgen(e)

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

