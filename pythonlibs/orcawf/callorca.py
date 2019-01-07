
import os, subprocess, shutil
import sys,socket
import multiprocessing
from orcaloader import load_calc_list

orca_command = '/home/vama/soft/orca/orca_3_0_3_linux_x86-64/orca'

properties = {}

def main():
    mp_name= 'c1.inp'
    #run_orca(mp_name)
    read_orcaout()
    #print (properties['totale'])


def run_orca(mp_name):
    arglist = [orca_command,mp_name]
    outputname = 'zindo.out'
    outfile = open(outputname,"w")
    p = subprocess.Popen(arglist, stdout=outfile )
    p.wait()

def read_orcaout():
    #calc = {}
    job_dir = os.getcwd()
    calc = load_calc_list(job_dir)
    print calc
#   print coord


if __name__ == "__main__":
   main()

# qmwf : quantum mechanics workflow for data science
# author: alvarovm at gihub

