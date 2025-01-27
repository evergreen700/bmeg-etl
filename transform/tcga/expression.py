from collections import defaultdict
import csv
from glob import glob
import gzip
import os.path
import logging
import subprocess
import sys

from bmeg import (GeneExpression, TranscriptExpression, Aliquot, Project,
                  GeneExpression_Aliquot_Aliquot, TranscriptExpression_Aliquot_Aliquot)

from bmeg.emitter import JSONEmitter
from bmeg.util.cli import default_argument_parser
from bmeg.util.logging import default_logging


def transform(source_path,
              id_map_file="source/tcga/expression/transcript-level/TCGA_ID_MAP.csv",
              emitter_directory="tcga"):

    # check if we are doing one file at time
    p, file_name = os.path.split(source_path)
    prefix = file_name.split('_')[1]
    emitter = JSONEmitter(directory=emitter_directory, prefix=prefix)
    logging.info('processing file {}'.format(source_path))
    logging.debug('individual file prefix {}'.format(prefix))

    # Map CGHub analysis IDs to GDC Aliquot IDs
    r = csv.DictReader(open(id_map_file))
    id_map = {}
    project_map = {}
    for row in r:
        id_map[row["CGHubAnalysisID"]] = row["Aliquot_id"].lower()
        project_map[row["CGHubAnalysisID"]] = "TCGA-" + row["Disease"]

    reader = csv.reader(gzip.open(source_path, "rt"), delimiter="\t")
    header = next(reader)
    samples = header[1:]

    # collect expression for all aliquots and transcripts
    collect = defaultdict(dict)
    collect_gene_vals = defaultdict(dict)

    for row in reader:
        feature_ids = row[0].split("|")
        transcript_id = feature_ids[0].split(".")[0]
        gene_id = feature_ids[1].split(".")[0]

        for cghub_id, raw_expr in zip(samples, row[1:]):
            expr = float(raw_expr)
            aliquot_id = id_map[cghub_id]
            project_id = project_map[cghub_id]
            collect[aliquot_id][transcript_id] = expr
            if gene_id not in collect_gene_vals[aliquot_id]:
                collect_gene_vals[aliquot_id][gene_id] = expr
            else:
                collect_gene_vals[aliquot_id][gene_id] += expr

    for aliquot_id, values in collect.items():
        t = TranscriptExpression(
            id=TranscriptExpression.make_gid(aliquot_id),
            metric="TPM",
            method="Illumina Hiseq",
            values=values,
            project_id=Project.make_gid(project_id)
        )
        emitter.emit_vertex(t)
        emitter.emit_edge(
            TranscriptExpression_Aliquot_Aliquot(
                from_gid=t.gid(),
                to_gid=Aliquot.make_gid(aliquot_id)
            ),
            emit_backref=True
        )

        geneValues = collect_gene_vals[aliquot_id]
        g = GeneExpression(
            id=GeneExpression.make_gid(aliquot_id),
            metric="TPM",
            method="Illumina Hiseq",
            values=geneValues,
            project_id=Project.make_gid(project_id)
        )
        emitter.emit_vertex(g)
        emitter.emit_edge(
            GeneExpression_Aliquot_Aliquot(
                from_gid=g.gid(),
                to_gid=Aliquot.make_gid(aliquot_id)
            ),
            emit_backref=True
        )

    emitter.close()


def make_parallel_workstream(source_path, jobs, dry_run=False):
    """ equivalent of: ls -1 source/tcga/expression/transcript-level/TCGA_*_tpm.tsv.gz | parallel --jobs 10 python3.7 transform/tcga/expression.py --source_path """
    with open('/tmp/tcga_expression_transform.txt', 'w') as outfile:
        for path in glob(source_path):
            outfile.write("{}\n".format(path))
    try:
        cmd = 'cat /tmp/tcga_expression_transform.txt | parallel --jobs {} {} {} --source_path'.format(jobs, sys.executable, __file__)
        logging.info('running {}'.format(cmd))
        if not dry_run:
            subprocess.check_output(cmd, shell=True)
        else:
            return cmd
    except subprocess.CalledProcessError as run_error:
        logging.exception(run_error)
        raise ValueError("error code {} {}".format(run_error.returncode, run_error.output))


if __name__ == "__main__":
    parser = default_argument_parser()
    parser.add_argument("--source_path", default="source/tcga/expression/transcript-level/*_tpm.tsv.gz", help="path to file(s)")
    parser.add_argument("--jobs", default=4, help="number of jobs to run in parallel")
    options = parser.parse_args()
    default_logging(options.loglevel)
    if '*' in options.source_path:
        make_parallel_workstream(source_path=options.source_path, jobs=options.jobs)
    else:
        transform(source_path=options.source_path)
