#!/usr/bin/env python3

import sys
import csv
import h5py
import argparse
from bmeg.vertex import GeneExpression, Aliquot, ExpressionMetric
from bmeg.emitter import JSONEmitter

if __name__ == "__main__":
    #parser = argparse.add_arg("--h5")
    #args = parser.parse_args()

    meta_file = "source/lincs/LDS-1194/Metadata/Small_Molecule_Metadata.txt"
    src_id_col = "sm_center_batch_id"
    dst_id_col = "sm_pubchem_cid"
    emitter = JSONEmitter("lincs-1194")

    chem_table = {}
    with open(meta_file, "rt") as handle:
        reader = csv.DictReader(handle, delimiter="\t")
        for row in reader:
            chem_table[row[src_id_col]] = row[dst_id_col]
    #print(chem_table)
    #print("BRD-K37049577-001-04-4" in chem_table)
    #print(b'BRD-K37049577-001-04-4' in chem_table)
    h5 = "source/lincs/LDS-1194/Data/zspc_n70323x22268.gctx"
    f = h5py.File(h5, 'r')

    gene_symbols = list(map(lambda x:x.tostring().decode(), f['0']['META']['ROW']['pr_gene_symbol']))
    #print(list(f['0']['META']['COL']))
    #sys.exit(0)
    #print(list(f['0']['META']['COL']['id']))
    #print(list(f['0']['META']['COL']['cell_id']))
    chem_ids = []
    for p in f['0']['META']['COL']['pert_id']:
        pid = p.tostring().decode()
        if pid != "DMSO":
            chem_ids.append(chem_table[pid])
        else:
            chem_ids.append("DMSO")

    matrix = f['0']['DATA']['0']['matrix']
    i = 0
    for id, cell_id, chem_id, dose, time in zip(f['0']['META']['COL']['id'], f['0']['META']['COL']['cell_id'], chem_ids, f['0']['META']['COL']['pert_dose'], f['0']['META']['COL']['pert_time']):
        #print(i)
        exp = matrix[i]
        data = list(zip(gene_symbols, list(map(lambda x:float(x), exp))))
        d = dict(list(zip(gene_symbols, list(map(lambda x:float(x), exp)))))
        print(len(exp), len(gene_symbols), len(d), len(list(zip(gene_symbols, list(map(lambda x:float(x), exp))))))
        out = GeneExpression(id=id.tostring().decode(), metric=ExpressionMetric.LOG, method="L1000", values=d, source="LINCS")
        emitter.emit_vertex(out)
        i += 1
    """
    m = f['0']['DATA']['0']['matrix']
    for row in m:
        d = dict(zip(gene_symbols, row))
        print(d)
    """
