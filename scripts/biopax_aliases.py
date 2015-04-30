#!/usr/bin/env python

import rdflib
import sys
from glob import glob
import os
from multiprocessing import Pool


def scan_biopax_file(path):
    g = rdflib.Graph()
    g.parse(path)
    out = []
    skip = {}
    #we're looking for the root pathway. This assumes there is only on pathway
    #description in the file, and any other pathways are 'components'
    for a in g.query("""
SELECT ?path WHERE {
    ?path a <http://www.biopax.org/release/biopax-level3.owl#Pathway> .
    ?other ?something ?path .
}
            """):
        skip[a[0]] = True

    for a in g.query("""
SELECT ?db ?id ?path WHERE {
    ?path a <http://www.biopax.org/release/biopax-level3.owl#Pathway> .
    ?path <http://www.biopax.org/release/biopax-level3.owl#xref> ?xref .
    ?xref <http://www.biopax.org/release/biopax-level3.owl#db> ?db .
    ?xref <http://www.biopax.org/release/biopax-level3.owl#id> ?id
}
            """):
        if a[2] not in skip:
            out.append( [ os.path.basename(path), str(a[0]), str(a[1]) ] )
    for a in g.query("""
SELECT ?dataSource ?name ?path WHERE {
    ?path a <http://www.biopax.org/release/biopax-level3.owl#Pathway> .
    ?path <http://www.biopax.org/release/biopax-level3.owl#dataSource> ?dataSource .
    ?path <http://www.biopax.org/release/biopax-level3.owl#name> ?name .
}
            """):
        if a[2] not in skip:
            out.append( [ os.path.basename(path), os.path.basename(a[0]), str(a[1]) ] )
    return out

def scan(indir):
    fileset = glob(os.path.join(indir, "*.owl"))

    p = Pool(8)
    out = p.map(scan_biopax_file, fileset)
    for scan in out:
        for path, db, dbid in scan:
            yield (path, db, dbid)

if __name__ == "__main__":
    indir = sys.argv[1]
    for path, db, dbid in scan(indir):
        print "%s\t%s\t%s" % (path, db, dbid)
