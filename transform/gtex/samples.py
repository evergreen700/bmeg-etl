from bmeg.util.cli import default_argument_parser
from bmeg.emitter import JSONEmitter
from bmeg.ioutils import read_tsv
from bmeg.vertex import Biosample, Project, Individual
from bmeg.edge import BiosampleFor, InProject


parser = default_argument_parser()
parser.add_argument("samples_file")
parser.add_argument("individuals_file")


def extract_individual_id(sample_id):
    return "-".join(sample_id.split("-")[:2])


def transform(emitter, samples, individuals):
    project = Project("gtex", gdc_attributes={})
    emitter.emit_vertex(project)

    for row in individuals:
        individual_id = row["SUBJID"]
        i = Individual(
            individual_id,
            gdc_attributes={},
            gtex_attributes=row,
        )
        emitter.emit_vertex(i)
        emitter.emit_edge(
            InProject(),
            i.gid(),
            project.gid(),
        )

    for row in samples:
        sample_id = row["SAMPID"]
        individual_id = extract_individual_id(sample_id)
        b = Biosample(
            sample_id,
            gdc_attributes={},
            gtex_attributes=row,
        )
        emitter.emit_vertex(b)
        emitter.emit_edge(
            BiosampleFor(),
            b.gid(),
            Individual.make_gid(individual_id),
        )


if __name__ == "__main__":
    args = parser.parse_args()

    e = JSONEmitter("gtex")
    s = read_tsv(args.samples_file)
    i = read_tsv(args.individuals_file)

    transform(e, s, i)

    e.close()
