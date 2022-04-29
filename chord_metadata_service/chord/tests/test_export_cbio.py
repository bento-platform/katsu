import uuid
import io
from typing import Dict, TextIO
from os import walk, path

from django.db.models import F
from django.test import TestCase

from chord_metadata_service.chord.export_cbio import (
    CBIO_FILES_SET,
    PATIENT_DATA_FILENAME,
    PATIENT_DATATYPE,
    SAMPLE_DATA_FILENAME,
    SAMPLE_DATATYPE,
    clinical_meta_export,
    individual_export,
    sample_export,
    study_export,
    study_export_meta
)
from chord_metadata_service.chord.data_types import DATA_TYPE_PHENOPACKET, DATA_TYPE_EXPERIMENT
from chord_metadata_service.chord.export_utils import ExportFileContext
from chord_metadata_service.chord.models import Project, Dataset, TableOwnership, Table
# noinspection PyProtectedMember
from chord_metadata_service.chord.ingest import (
    WORKFLOW_PHENOPACKETS_JSON,
    WORKFLOW_INGEST_FUNCTION_MAP,
)
from chord_metadata_service.patients.models import Individual
from chord_metadata_service.phenopackets import models as PhModel


from .constants import VALID_DATA_USE_1
from .example_ingest import (
    EXAMPLE_INGEST_PHENOPACKET,
    EXAMPLE_INGEST_OUTPUTS,
)


class ExportCBioTest(TestCase):
    def setUp(self) -> None:
        # Creates a test database and populate with a phenopacket test file

        p = Project.objects.create(title="Project 1", description="")
        self.d = Dataset.objects.create(title="Dataset 1", description="Some dataset", data_use=VALID_DATA_USE_1,
                                        project=p)
        self.study_id = str(self.d.identifier)

        # TODO: Real service ID
        # table for phenopackets
        to = TableOwnership.objects.create(table_id=uuid.uuid4(), service_id=uuid.uuid4(), service_artifact="metadata",
                                           dataset=self.d)
        self.t = Table.objects.create(ownership_record=to, name="Table 1", data_type=DATA_TYPE_PHENOPACKET)

        # table for experiments metadata
        to_exp = TableOwnership.objects.create(table_id=uuid.uuid4(), service_id=uuid.uuid4(),
                                               service_artifact="experiments", dataset=self.d)
        self.t_exp = Table.objects.create(ownership_record=to_exp, name="Table 2", data_type=DATA_TYPE_EXPERIMENT)

        self.p = WORKFLOW_INGEST_FUNCTION_MAP[WORKFLOW_PHENOPACKETS_JSON](EXAMPLE_INGEST_OUTPUTS, self.t.identifier)

        # Update the last sample to remove direct reference to any individual.
        # In that case, Sample and Individual are cross referenced through the
        # Phenopacket model.
        PhModel.Biosample.objects.filter(
                id=EXAMPLE_INGEST_PHENOPACKET["biosamples"][-1]["id"]
            ).update(individual=None)

    def stream_to_dict(self, output: TextIO) -> Dict[str, str]:
        """
        Utility function. Parses cBioPortal meta data text files (lines of
        key/value pairs separated by `: `) in a dictionary structure.
        """
        output.seek(0)
        content = dict()
        for line in output:
            key, value = line.rstrip().split(': ')
            content[key] = value
        return content

    def test_file_creation(self):
        """
        Check files creation.
        Files content is tested subsequently with each file generating function.
        """

        with ExportFileContext(None, self.study_id) as file_export:
            study_export(file_export.get_path, self.study_id)
            export_dir = file_export.get_path()
            self.assertTrue(path.exists(export_dir))
            for (dirpath, dirnames, filenames) in walk(export_dir):
                filesSet = {*filenames}
                self.assertTrue(CBIO_FILES_SET.issubset(filesSet))
                break   # do not recurse the directory tree

    def test_export_cbio_study_meta(self):
        with io.StringIO() as output:
            study_export_meta(self.d, output)
            content = self.stream_to_dict(output)

        self.assertIn('type_of_cancer', content)
        self.assertEqual(content['cancer_study_identifier'], self.study_id)
        self.assertEqual(content['name'], self.d.title)
        self.assertEqual(content['description'], self.d.description)

    def test_export_cbio_sample_meta(self):
        with io.StringIO() as output:
            clinical_meta_export(self.study_id, SAMPLE_DATATYPE, output)
            content = self.stream_to_dict(output)

        self.assertEqual(content['cancer_study_identifier'], self.study_id)
        self.assertEqual(content['genetic_alteration_type'], 'CLINICAL')
        self.assertEqual(content['datatype'], 'SAMPLE_ATTRIBUTES')
        self.assertEqual(content['data_filename'], SAMPLE_DATA_FILENAME)

    def test_export_cbio_patient_meta(self):
        with io.StringIO() as output:
            clinical_meta_export(self.study_id, PATIENT_DATATYPE, output)
            content = self.stream_to_dict(output)

        self.assertEqual(content['cancer_study_identifier'], self.study_id)
        self.assertEqual(content['genetic_alteration_type'], 'CLINICAL')
        self.assertEqual(content['datatype'], 'PATIENT_ATTRIBUTES')
        self.assertEqual(content['data_filename'], PATIENT_DATA_FILENAME)

    def test_export_cbio_patient_data(self):
        indiv = Individual.objects.filter(phenopackets=self.p)
        with io.StringIO() as output:
            individual_export(indiv, output)
            # Check header
            output.seek(0)
            field_count = None
            field_names = []
            for i, line in enumerate(output):
                # 4 first header lines begin with `#`
                if i < 4:
                    self.assertEqual(line[0], '#')
                    continue

                # Following lines are regular TSV formatted lines
                pieces = line.rstrip().split('\t')

                # 5th line is a header with predefined field names
                if i == 4:
                    field_count = len(pieces)
                    field_names = pieces

                    # At least PATIENT_ID and SEX
                    self.assertGreaterEqual(field_count, 2)
                    self.assertIn('PATIENT_ID', pieces)
                    continue

                # TSV body. Inspect first line and break
                self.assertEqual(field_count, len(pieces))
                record = dict(zip(field_names, pieces))

                self.assertEqual(record["PATIENT_ID"], EXAMPLE_INGEST_PHENOPACKET["subject"]["id"])
                self.assertEqual(record["SEX"], EXAMPLE_INGEST_PHENOPACKET["subject"]["sex"])
                break

    def test_export_cbio_sample_data(self):
        samples = PhModel.Biosample.objects.filter(phenopacket=self.p)\
            .annotate(phenopacket_subject_id=F("phenopacket__subject"))
        with io.StringIO() as output:
            sample_export(samples, output)
            # Check header
            output.seek(0)
            field_count = None
            field_names = []
            sample_count = 0
            for i, line in enumerate(output):
                # 4 first header lines begin with `#`
                if i < 4:
                    self.assertEqual(line[0], '#')
                    continue

                # Following lines are regular TSV formatted lines
                pieces = line.rstrip().split('\t')

                # 5th line is a header with predefined field names
                if i == 4:
                    field_count = len(pieces)
                    field_names = pieces

                    # At least PATIENT_ID and SAMPLE_ID
                    self.assertGreaterEqual(field_count, 2)
                    self.assertIn('PATIENT_ID', pieces)
                    self.assertIn('SAMPLE_ID', pieces)
                    continue

                # TSV body: 1 row per sample
                self.assertEqual(field_count, len(pieces))
                record = dict(zip(field_names, pieces))

                self.assertEqual(
                    record["PATIENT_ID"],
                    EXAMPLE_INGEST_PHENOPACKET["biosamples"][sample_count]["individual_id"]
                )
                self.assertEqual(
                    record["SAMPLE_ID"],
                    EXAMPLE_INGEST_PHENOPACKET["biosamples"][sample_count]["id"]
                )
                sample_count += 1

            self.assertEqual(sample_count, samples.count())
