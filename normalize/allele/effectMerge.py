#!/usr/bin/env python

import pandas as pd
import polars as pl
import argparse
import json

parser = argparse.ArgumentParser(description="Basically annotates a vcf of allele effects using the amino acid equivalent of a bed file")
parser.add_argument("-f", "--featuresFile", help="json.gz of features to match up (has transcript, start and end cols)")
parser.add_argument("-v", "--variantsFile", help="json.gz of variants to match up (has ensembl_transcript and aa_position cols")
args = parser.parse_args()

features = pl.from_pandas(pd.read_json(args.featuresFile, lines=True))
variants = pl.from_pandas(pd.read_json(args.variantsFile, lines=True))
var1 = variants.filter(pl.col('aa_ref').is_not_null())
merge1 = var1[0:100].join(features, left_on='ensembl_transcript', right_on='transcript', how='left')

merge2 = merge1.filter(pl.col('aa_position').is_between(pl.col('start'),pl.col('end'))).sort('id').select(pl.all().exclude('start','end'))

merge3 = merge2.groupby('id').agg(pl.all().drop_nulls().explode().unique().first())
#merge2.groupby('id').agg(pl.all().drop_nulls().explode().unique().cast(pl.Utf8).str.concat(', '))

for row in merge3.iter_rows(named=True):
  rowd = {k:v for k,v in row.items() if v is not None}
  #if "sampleid" in rowd and "treatmentid" in rowd:
  print(json.dumps(rowd))
for row in variants.filter(pl.col('aa_ref').is_null()).iter_rows(named=True):
  rowd = {k:v for k,v in row.items() if v is not None}
  #if "sampleid" in rowd and "treatmentid" in rowd:
  print(json.dumps(rowd))
