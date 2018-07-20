# pdbsearch :: Python powered search facilities for the RCSB protein databank
---

The RCSB protein databank offers a powerful RESTful service for searching
structures. _pdbsearch_ provides a simple interface to bring the search
facility to the command-line or into a Python script or Jupyter notebook.
The central element is the PDBQuery class, which can be instantiated with
a single query, and can subsequently be combined with other queries using
& (and) and | (or)::

    import pdbsearch
    query = pdbsearch.PDBQ_Ligand('ATP')
    query |= pdbsearch.PDBQ_Refine(90)
    query.search() # Returns a list of PDBIDs
    for pdbid, data in query.downloads():
        ... # process data from file

The downloading generator will catch HTTP errors, like 404, reporting them,
but passing over, as these must have arisen from a discrepancy between the
listing of PDB IDs provided by RCSB and the files there available. Those
errors can thus not be accounted to the _pdbsearch_ and probably not to the
connection.

When run as script, the functionality is currently limited to ligand based
search, with an optional argument for setting the similarity cutoff to discard
homologous proteins.

This is the first version of this script and additional functionality
will be added, including more search options, and a more complete
command-line interface.

