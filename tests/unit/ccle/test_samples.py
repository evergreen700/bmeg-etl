
import os
import contextlib
import pytest
from transform.ccle.samples import transform
from bmeg.vertex import Biosample, Aliquot, Individual, Project, Phenotype

EXPECTED_PROJECT_GIDS = [
    "Project:CCLE:HAEMATOPOIETIC_AND_LYMPHOID_TISSUE",
    "Project:CCLE:CENTRAL_NERVOUS_SYSTEM",
    "Project:CCLE:PROSTATE",
    "Project:CCLE:STOMACH",
    "Project:CCLE:URINARY_TRACT",
    "Project:CCLE:SKIN"
]


@pytest.fixture
def emitter_path_prefix(request):
    """ get the full path of the test output """
    return os.path.join(request.fspath.dirname, 'test')


@pytest.fixture
def sample_info_file(request):
    """ get the full path of the test output """
    return os.path.join(request.fspath.dirname, 'source/ccle/DepMap-2018q3-celllines.csv')


def validate(helpers, emitter_path_prefix, sample_info_file):
    """ run xform and test results"""
    biosample_file = os.path.join(emitter_path_prefix, 'Biosample.Vertex.json.gz')
    aliquot_file = os.path.join(emitter_path_prefix, 'Aliquot.Vertex.json.gz')
    aliquotfor_file = os.path.join(emitter_path_prefix, 'AliquotFor.Edge.json.gz')
    individual_file = os.path.join(emitter_path_prefix, 'Individual.Vertex.json.gz')
    project_file = os.path.join(emitter_path_prefix, 'Project.Vertex.json.gz')
    in_project_file = os.path.join(emitter_path_prefix, 'InProject.Edge.json.gz')
    biosample_for_file = os.path.join(emitter_path_prefix, 'BiosampleFor.Edge.json.gz')
    phenotype_file = os.path.join(emitter_path_prefix, 'Phenotype.Vertex.json.gz')
    phenotype_of_file = os.path.join(emitter_path_prefix, 'PhenotypeOf.Edge.json.gz')

    all_files = [biosample_file, aliquot_file, aliquotfor_file, individual_file, project_file, in_project_file, biosample_for_file, phenotype_file, phenotype_of_file]
    # remove output
    with contextlib.suppress(FileNotFoundError):
        for f in all_files:
            os.remove(f)

    # create output
    transform(path=sample_info_file, prefix=emitter_path_prefix)

    # test.Biosample.Vertex.json
    helpers.assert_vertex_file_valid(Biosample, biosample_file)
    # test.Aliquot.Vertex.json
    helpers.assert_vertex_file_valid(Aliquot, aliquot_file)
    # test.Individual.Vertex.json
    individual_count = helpers.assert_vertex_file_valid(Individual, individual_file)
    assert individual_count == 9, 'expected individual_count'
    # test.Project.Vertex.json
    project_count = helpers.assert_vertex_file_valid(Project, project_file)
    assert project_count == len(EXPECTED_PROJECT_GIDS), 'expected project_count'

    # test.AliquotFor.Edge.json
    helpers.assert_edge_file_valid(Aliquot, Biosample, aliquotfor_file)

    # test.PhenotypeOf.Edge.json
    helpers.assert_edge_file_valid(Aliquot, Phenotype, phenotype_of_file)

    # validate vertex for all edges exist
    helpers.assert_edge_joins_valid(all_files)


def test_simple(helpers, emitter_path_prefix, sample_info_file):
    """ limit the result to a single project"""
    validate(helpers, emitter_path_prefix, sample_info_file)
