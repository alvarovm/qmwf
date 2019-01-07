#!/usr/bin/env python2
# -*- coding: utf-8 -*-

"""
Created on Tue Jul 18 13:17:36 2017

@author: vama
"""


import logging
from cclib.parser.utils import PeriodicTable, convertor
from cclib.parser import ccopen
from os.path import join

from munch import Munch


def load_calc_list(job_dir, pname='nwchem.out', context=None) :

    meta_data = Munch()
    calc = Munch(meta_data= meta_data,
                 properties = Munch())


    outfile = join(job_dir,pname)
    myfile = ccopen(outfile)

    #myfile.logger.setLevel(logging.ERROR)

    data = myfile.parse()

    t = PeriodicTable()


#   Vdd calc
#    print     data.nmo
#    print data.moenergies[-1]
#    print data.homos
#    print data.scfenergies[-1]

    if 'optdone' in data.__dict__:
        calc.optdone = data.optdone
        if context == 'opt':
             return calc
    else:
        calc.optdone = None
        if len(data.scfenergies) > 0:
            calc.optdone = False
        else:
            calc.optdone = None
#       return calc

    if calc.optdone :
        meta_data.version = data.metadata['package_version']

        meta_data.program = data.metadata['package']
        #meta_data.wall_clock_time = data.walltime
        #meta_data.wall_clock_time = data.walltime

        meta_data.worker_name = pname

        calc.theory = data.metadata['methods'][-1]
        calc.functional = data.metadata['functional']
        calc.basisset = data.metadata['basis_set']

        calc.properties.total_energy = convertor(data.scfenergies[-1],"eV", "hartree")
    #    calc.properties.total_energy =  data.scfenergies[-1]

        nmotot = data.nmo
        numoc = len(data.nooccnos[-1])
        low=len(data.moenergies[-1]) - numoc
        newmoe = data.moenergies[-1][low:nmotot]
        newmoe =convertor(data.moenergies[-1],"eV", "hartree")[low:nmotot]
        occ = []
        unocc = []
        for index, value in enumerate(data.nooccnos[-1]):
            if value != 0.0:
                occ_info = dict(method="rhf", spin="alpha", type="occ", number=index+1, energy=newmoe[index])
                occ.append(occ_info)
            else:
                unocc_info = dict(method="rhf", spin="alpha", type="unocc", number=index+1, energy=newmoe[index])
                unocc.append(unocc_info)
        for index, value in enumerate(data.nooccnos[-1]):
            if value == 0.0:
                lumo = newmoe[index]
                homo = newmoe[index-1]
                break
    #
        calc.properties.homo= homo
        calc.properties.lumo = lumo
        calc.properties.gap = lumo-homo
        #calc.properties.electric_dipole_moment_norm
        calc.properties.occupied_orbital_number = len(occ)
        calc.orbital_energy_list = occ + unocc

    coords = []
    for index, value in enumerate(data.atomcoords[-1]):
        x, y, z = value
        elem = t.element[data.atomnos[index]]
        coords.append(dict(element=elem, x=x, y=y, z=z))
    calc.coords = coords

    return calc


def main():
    from os import getcwd

    result = {}
    calc = load_calc_list(getcwd(), context=None)
    result.update(calc)
    print result


if __name__ == "__main__":
       main()
# qmwf : quantum mechanics workflow for data science
# author: alvarovm at gihub

