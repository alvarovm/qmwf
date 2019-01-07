
import os, subprocess, shutil
import sys, socket
import multiprocessing
from external_libs import bgqtools
import time
#import mopac

#nwchem_command = '/home/vama/chem2/nwchem/nwchem-6.6/nwchem-6/bin/LINUX64/nwchem'
#nwchem_command = '/home/vama/soft/nwchem/nwchem-6.6/bin/LINUX64/nwchem'

#In VESTA
#nwchem_command ='/home/avazquez/fs0/soft/nwchem/testintel/nwchem-6.5/bin/BGQ/nwchem'
#nwchem_command ='/gpfs/vesta-fs0/projects/catalyst/avazquez/test/nwchem/benchmarck/dft/test-66/nwchem66'


#bin=/home/avazquez/fs0/test/nwchem/benchmarck/dft/test-66/nwchem66

properties = {}

def main():
    #name should be nwchem.nw
    mp_name= 'nwchem'
    #read_arc(mp_name)
    #print (properties['totale'])
    jobdetails = {}
    jobdetails['modes'] = 8
    jobdetails['thres'] = 1
    partsize, partition, job_id = bgqtools.get_cobalt_info()
    jobdetails['block_size']  = partsize
    jobdetails['block']  = partition
    run_nwchem(mp_name, jobdetails)

def run_nwchem(mp_name, jobdetails):

    nps = jobdetails['modes'] * jobdetails['block_size']
    arglist=["runjob",
		"--np", str(nps),
		"-p", str(jobdetails['modes']),
		"--envs", "OMP_NUM_THREADS=" + str(jobdetails['thres']),
		"--verbose", "INFO",
		"--block", jobdetails['block'],
		":",
		nwchem_command]

    outputname = mp_name + '.out'
    outfile = open(outputname,"w")
    p = subprocess.Popen(arglist, stdout=outfile )
    time.sleep(5)
    try:
   	status=p.poll()
    except:
        write_log("%s : Replica %s sub-block failure. Exiting" % jobdetails['pname'])
        return False

#   with open(outputname, 'w') as fd:
#      fd.write(p.communicate()[0])
#   result = p.communicate()[0]
    p.wait()
    return True

def run_nwchem_sub(mp_name, jobdetails):

    #print jobdetails
    jobdetails['thres'] = 2
    nwchem_command = jobdetails['binary']

    nps = int(jobdetails['modes']) * int(jobdetails['nodes_per_replica'])
    arglist=["runjob","--np", str(nps),
			"-p", str(jobdetails['modes']),
			"--shape", str(jobdetails['shape']),
			"--block", str(jobdetails['block']),
			"--corner", str(jobdetails['corner']),
		   	"--envs", "BG_SMP_FAST_WAKEUP=YES",
		   	"--envs", "OMP_WAIT_POLICY=ACTIVE",
		   	"--envs", "OMP_NUM_THREADS=" + str(jobdetails['thres']),
			"--verbose", "INFO",
			":", str(nwchem_command)]

    outputname = mp_name + '.out'
    outfile = open(outputname,"w")
    p = subprocess.Popen(arglist, stdout=outfile )
    time.sleep(5)
    try:
        status=p.poll()
    except:
        write_log("%s : Replica %s sub-block failure. Exiting" % jobdetails['pname'])
        return False

    p.wait()
    return True

def read_out(mp_name):
    outpath = mp_name +'.out'
    with open(outpath, 'r') as fp:
      loglines = fp.readlines()
    return loglines

if __name__ == "__main__":
   main()

# qmwf : quantum mechanics workflow for data science
# author: alvarovm at gihub

