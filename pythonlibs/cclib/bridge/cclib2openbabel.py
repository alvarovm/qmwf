# -*- coding: utf-8 -*-
#
# Copyright (c) 2016, the cclib development team
#
# This file is part of cclib (http://cclib.github.io) and is distributed under
# the terms of the BSD 3-Clause License.

"""Bridge between cclib data and openbabel (http://openbabel.org)."""

try:
    import openbabel as ob
except ImportError:
    # Fail silently for now.
    pass

from cclib.parser.data import ccData


def makeopenbabel(atomcoords, atomnos, charge=0, mult=1):
    """Create an Open Babel molecule.

    >>> import numpy, openbabel
    >>> atomnos = numpy.array([1, 8, 1], "i")
    >>> coords = numpy.array([[-1., 1., 0.], [0., 0., 0.], [1., 1., 0.]])
    >>> obmol = makeopenbabel(coords, atomnos)
    >>> obconversion = openbabel.OBConversion()
    >>> formatok = obconversion.SetOutFormat("inchi")
    >>> print obconversion.WriteString(obmol).strip()
    InChI=1/H2O/h1H2
    """
    obmol = ob.OBMol()
    for i in range(len(atomnos)):
        # Note that list(atomcoords[i]) is not equivalent!!!
        # For now, only take the last geometry.
        # TODO: option to export last geometry or all geometries?
        coords = atomcoords[-1][i].tolist()
        atomno = int(atomnos[i])
        obatom = ob.OBAtom()
        obatom.SetAtomicNum(atomno)
        obatom.SetVector(*coords)
        obmol.AddAtom(obatom)
    obmol.ConnectTheDots()
    obmol.PerceiveBondOrders()
    obmol.SetTotalSpinMultiplicity(mult)
    obmol.SetTotalCharge(int(charge))
    return obmol

def makecclib(mol):
    """Create cclib attributes and return a ccData from an OpenBabel molecule.

    Beyond the numbers, masses and coordinates, we could also set the total charge
    and multiplicity, but often these are calculated from atomic formal charges
    so it is better to assume that would not be correct.
    """

    attributes = {
        'atomcoords':   [],
        'atommasses':   [],
        'atomnos':      [],
        'natom':        mol.NumAtoms(),
    }
    for atom in ob.OBMolAtomIter(mol):
        attributes['atomcoords'].append([atom.GetX(), atom.GetY(), atom.GetZ()])
        attributes['atommasses'].append(atom.GetAtomicMass())
        attributes['atomnos'].append(atom.GetAtomicNum())
    return ccData(attributes)

def readfile(fname, format):
    """Read a file with OpenBabel and extract cclib attributes."""

    obc = ob.OBConversion()
    if obc.SetInFormat(format):
        mol = ob.OBMol()
        obc.ReadFile(mol, fname)
        return makecclib(mol)
    else:
        print("Unable to load the %s reader from OpenBabel." % format)
        return {}


if __name__ == "__main__":
    import doctest
    doctest.testmod()
# qmwf : quantum mechanics workflow for data science
# author: alvarovm at gihub

