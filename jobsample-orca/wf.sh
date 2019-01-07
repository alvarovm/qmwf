#!/bin/bash

export THISDIR=/home/vama/soft/python-tests/qmwf
export PYTHONPATH=${THISDIR}/pythonlibs:$PYTHONPATH
unset LD_PRELOAD
rm -rf log output inbox
cp -R inbox.bk inbox
/home/vama/miniconda2/envs/chemchem/bin/python ${THISDIR}/pythonlibs/wflauncher.py confwf.json
