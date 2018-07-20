#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
This program/module facilitates posting queries to the RCSB Protein databank.
The script is currently limited to perform searches on ligand name. An
optional argument can be provided as similarity cutoff to exclude 
homologous proteins. The PDB structures found are automatically downloaded.

Usage:
    pdbsearch.py ligand [cutoff]

TODO:
    This program/module will be extended in the near future to

        #. bring more of the PDB search facilities to the command-line
        #. provide a full command-line interface for searching/listing/downloading
"""

__author__ = 'Tsjerk A. Wassenaar'
__copyright__ = 'Copyright 2018, University of Groningen'
__version__ = '0.1.0dev0'
__license__ = 'Apache License 2.0'


## IMPORTS

import sys
from urllib.error import HTTPError
import urllib.request as urllib


## CONSTANTS

PDB = 'http://www.rcsb.org/pdb/'
PDBREST = PDB + 'rest/search'
PDBDOWN = PDB + 'download/downloadFile.do?fileFormat=pdb&compression=NO&structureId='

PDBREFINE = """
  <queryRefinement>
    <queryRefinementLevel>{level}</queryRefinementLevel>
    <conjunctionType>{conjunction}</conjunctionType>
    <orgPdbQuery>
      {query}
    </orgPdbQuery>
  </queryRefinement>
"""


## CLASSES
    
class PDBQuery:
    def __init__(self, query=None):
        self.ids = []
        self.query = []
        if query:
            self.query = ["or", query]
        
    def __and__(self, other):
        out = PDBQuery()
        out.query = self.query + ['and'] + other.query[1:]
        return out
        
    def __or__(self, other):
        out = PDBQuery()
        out.query = self.query + ['or'] + other.query[1:]
        return out

    def __str__(self):
        level = 0
        out = ['<orgPdbCompositeQuery version="1.0">']
        querit = iter(self.query)
        for item in querit:
            conjunction = item
            query = "\n      ".join(next(querit).split("\n"))
            out.append(PDBREFINE.format(**locals()))
            level += 1
        out.append('</orgPdbCompositeQuery>')
        return "\n".join(out)
    
    def search(self):
        f = urllib.urlopen(PDBREST, data=str(self).encode('utf-8'))
        self.ids = [ item.decode('utf-8') for item in f.read().split() ]
        if self.ids:
            print("Found number of PDB entries:", len(self.ids))
            return self.ids
        print("Failed to retrieve results")
        return None
    
    def download(self):
        if not self.ids:
            self.search()
        for pdbid in self.ids:
            try:
                print(pdbid, end=" ")
                yield pdbid, urllib.urlopen(PDBDOWN + pdbid).read()
            except HTTPError as e:
                sys.stderr.write("Failed retrieving {}:".format(pdbid))
                sys.stderr.write(e)
                continue

            
class PDBQ_Ligand(PDBQuery):
    """Ligand query for RCSB protein database"""
    def __init__(self, name, comparator="Contains", polymeric="Any"):
        PDBQuery.__init__(self)
        typ = "org.pdb.query.simple.ChemCompNameQuery"
        self.query = [
            "or", 
            (
                "<queryType>{typ}</queryType>\n"
                "<comparator>{comparator}</comparator>\n"
                "<name>{name}</name>\n"
                "<polymericType>{polymeric}</polymericType>"
            ).format(**locals())
        ]

        
class PDBQ_Refine(PDBQuery):
    """Query for refinement of PDB search result based on level of homology"""
    def __init__(self, level=90):
        PDBQuery.__init__(self)
        typ = "org.pdb.query.simple.HomologueReductionQuery"
        self.query = [
            "or",
            (
                "<queryType>{typ}</queryType>\n"
                "<identityCutoff>90</identityCutoff>"
            ).format(**locals())
        ]
        

## FUNCTIONS


## MAIN
def main(args):

    if len(args) < 2:
        ...
        return 1

    query = PDBQ_Ligand(args[1])
    if len(args) > 2:
        query |= PDBQ_Refine(int(args[2]))
        
    # Search and download PDB ids matching the query
    # Homology will 
    for pdbid, data in query.download():
        open("{}.pdb".format(pdbid), 'wb').write(data)

    return 0


if __name__ == "__main__":
    exco = main(sys.argv)
    sys.exit(exco)
