
import os, subprocess, shutil
import sys,socket
import multiprocessing
#import mopac

#nwchem_command = '/home/vama/chem2/nwchem/nwchem-6.6/nwchem-6/bin/LINUX64/nwchem'
nwchem_command = '/home/vama/soft/nwchem/nwchem-6.6/bin/LINUX64/nwchem'

properties = {}

def main():
    mp_name= 'agua'
    run_nwchem(mp_name)
    #read_arc(mp_name)
    #print (properties['totale'])


def run_nwchem(mp_name):
    print("hola")
    arglist = [nwchem_command,mp_name]
    outputname = mp_name + '.out'
    p = subprocess.Popen(arglist, stdout=subprocess.PIPE )
    with open(outputname, 'w') as fd:
        fd.write(p.communicate()[0])
#   result = p.communicate()[0]
    p.wait()


def read_out(mp_name):
    outpath = mp_name +'.out'
    with open(outpath, 'r') as fp:
      loglines = fp.readlines()
    return loglines

if __name__ == "__main__":
   main()

# qmwf : quantum mechanics workflow for data science
# author: alvarovm at gihub

