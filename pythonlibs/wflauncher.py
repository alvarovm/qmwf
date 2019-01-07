from paralell_launch import launch_parallel
from sys  import argv
from os.path import isfile
from os import getcwd
import json

thisdir = getcwd()

fileconfig = 'confwf.json'

def startwf(configfile):
      if isfile(configfile):
           with open(configfile, 'r') as f:
              config = json.load(f)
           config['fileconfig'] = configfile
           config['thisdir'] = thisdir
           launch_parallel(config)
      else:
          print ("check args: %s not fount" % configfile)


def main(configfile):
      if configfile == '' :
          configfile = fileconfig
      startwf(configfile)

if __name__ == "__main__":
      configfile=''
      configfile = argv[1]
      main(configfile)
# qmwf : quantum mechanics workflow for data science
# author: alvarovm at gihub

