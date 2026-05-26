import io
import uuid
from typing import TextIO
from os import walk, path
from unittest.mock import MagicMock

from asgiref.sync import async_to_sync
from django.db.models import F
from django.test import SimpleTestCase, TestCase

from chord_metadata_service.chord.export import cbioportal as exp
from chord_metadata_service.chord.export.cbioportal import CbioportalClinicalHeaderGenerator
from chord_metadata_service.chord.export.cbioportal import (
    CBIO_FILES_SET,
    MUTATION_DATA_FILENAME,
    PATIENT_DATA_FILENAME,
    PATIENT_DATATYPE,
    REGEXP_INVALID_FOR_ID,
    SAMPLE_DATA_FILENAME,
    SAMPLE_DATATYPE,
)
from chord_metadata_service.chord.export.utils import ExportError, ExportFileContext
from chord_metadata_service.chord.dataset_schema import KatsuDatasetModel
from chord_metadata_service.chord.models import Project, DatasetV2
from chord_metadata_service.experiments.models import ExperimentResult
from chord_metadata_service.chord.ingest import WORKFLOW_INGEST_FUNCTION_MAP
from chord_metadata_service.chord.ingest.experiments import ingest_derived_experiment_results
from chord_metadata_service.chord.workflows.metadata import (
    WORKFLOW_EXPERIMENTS_JSON,
    WORKFLOW_PHENOPACKETS_JSON,
)
from chord_metadata_service.logger import logger
from chord_metadata_service.patients.models import Individual
from chord_metadata_service.phenopackets import models as pm


from .constants import VALID_DATASET_V2_PRIMARY_CONTACT
from .example_ingest import (
    EXAMPLE_INGEST_EXPERIMENT,
    EXAMPLE_INGEST_EXPERIMENT_RESULT,
    EXAMPLE_INGEST_PHENOPACKET,
)


class ExportCBioTest(TestCase):
    def setUp(self) -> None:
        # Creates a test database and populate with a phenopacket test file

        p = Project.objects.create(title="Project 1", description="")
        schema = KatsuDatasetModel(
            schema_version="1.0",
            title="Dataset 1",
            description="Some dataset",
            primary_contact=VALID_DATASET_V2_PRIMARY_CONTACT,
            project=str(p.identifier),
            identifier=str(uuid.uuid4()),
        )
        self.d = DatasetV2.from_schema(schema)
        self.d.save()
        self.d.refresh_from_db()
        self.study_id = str(self.d.identifier)

        self.p = WORKFLOW_INGEST_FUNCTION_MAP[WORKFLOW_PHENOPACKETS_JSON](
            EXAMPLE_INGEST_PHENOPACKET, self.d.identifier, logger
        )
        # ingest list of experiments
        self.exp = WORKFLOW_INGEST_FUNCTION_MAP[WORKFLOW_EXPERIMENTS_JSON](
            EXAMPLE_INGEST_EXPERIMENT, self.d.identifier, logger
        )
        # append derived MAF files to experiment results
        ingest_derived_experiment_results(EXAMPLE_INGEST_EXPERIMENT_RESULT, self.d.identifier, logger)
        self.exp_res = ExperimentResult.objects.all()

    @staticmethod
    def stream_to_dict(output: TextIO) -> dict[str, str]:
        """
        Utility function. Parses cBioPortal metadata text files (lines of
        key/value pairs separated by `: `) in a dictionary structure.
        """
        output.seek(0)
        content = dict()
        for line in output:
            key, value = line.rstrip().split(": ")
            content[key] = value
        return content

    def test_file_creation(self):
        """
        Check files creation.
        Files content is tested subsequently with each file generating function.
        """

        with ExportFileContext(None, self.study_id) as file_export:
            async_to_sync(exp.study_export)(file_export.get_path, self.study_id)
            export_dir = file_export.get_path()
            self.assertTrue(path.exists(export_dir))

            # recursively walk the export dir to get the generated files
            files_set = set()
            for dirpath, dirnames, filenames in walk(export_dir):
                files_set.update([path.relpath(path.join(dirpath, fn), export_dir) for fn in filenames])

            self.assertTrue(CBIO_FILES_SET.issubset(files_set))

    def test_file_creation_study_dne(self):
        with ExportFileContext(None, self.study_id) as file_export:
            # random uuid - does not exist; raised by study_export
            with self.assertRaises(ExportError):
                async_to_sync(exp.study_export)(file_export.get_path, str(uuid.uuid4()))

    def test_export_cbio_study_meta(self):
        with io.StringIO() as output:
            exp.study_export_meta(self.d, output)
            content = self.stream_to_dict(output)

        self.assertIn("type_of_cancer", content)
        self.assertEqual(content["cancer_study_identifier"], self.study_id)
        self.assertEqual(content["name"], self.d.title)
        self.assertEqual(content["description"], self.d.data.get("description", ""))

    def test_export_cbio_sample_meta(self):
        with io.StringIO() as output:
            exp.clinical_meta_export(self.study_id, SAMPLE_DATATYPE, output)
            content = self.stream_to_dict(output)

        self.assertEqual(content["cancer_study_identifier"], self.study_id)
        self.assertEqual(content["genetic_alteration_type"], "CLINICAL")
        self.assertEqual(content["datatype"], "SAMPLE_ATTRIBUTES")
        self.assertEqual(content["data_filename"], SAMPLE_DATA_FILENAME)

    def test_export_cbio_patient_meta(self):
        with io.StringIO() as output:
            exp.clinical_meta_export(self.study_id, PATIENT_DATATYPE, output)
            content = self.stream_to_dict(output)

        self.assertEqual(content["cancer_study_identifier"], self.study_id)
        self.assertEqual(content["genetic_alteration_type"], "CLINICAL")
        self.assertEqual(content["datatype"], "PATIENT_ATTRIBUTES")
        self.assertEqual(content["data_filename"], PATIENT_DATA_FILENAME)

    def test_export_cbio_patient_data(self):
        indiv = Individual.objects.filter(phenopackets=self.p)
        with io.StringIO() as output:
            async_to_sync(exp.individual_export)(indiv, output)
            # Check header
            output.seek(0)
            field_count = None
            field_names = []
            for i, line in enumerate(output):
                # 4 first header lines begin with `#`
                if i < 4:
                    self.assertEqual(line[0], "#")
                    continue

                # Following lines are regular TSV formatted lines
                pieces = line.rstrip().split("\t")

                # 5th line is a header with predefined field names
                if i == 4:
                    field_count = len(pieces)
                    field_names = pieces

                    # At least PATIENT_ID and SEX
                    self.assertGreaterEqual(field_count, 2)
                    self.assertIn("PATIENT_ID", pieces)
                    continue

                # TSV body. Inspect first line and break
                self.assertEqual(field_count, len(pieces))
                record = dict(zip(field_names, pieces))

                # PATIENT_ID can't contain characters other than letters/numbers/hyphen/underscore
                self.assertTrue(REGEXP_INVALID_FOR_ID.search(record["PATIENT_ID"]) is None)
                self.assertEqual(record["PATIENT_ID"], exp.sanitize_id(EXAMPLE_INGEST_PHENOPACKET["subject"]["id"]))
                self.assertEqual(record["SEX"], EXAMPLE_INGEST_PHENOPACKET["subject"]["sex"])
                break

    def test_export_cbio_sample_data(self):
        samples = pm.Biosample.objects.filter(phenopackets=self.p)

        with io.StringIO() as output:
            async_to_sync(exp.sample_export)(samples, output)
            # Check header
            output.seek(0)
            field_count = None
            field_names = []
            sample_count = 0
            for i, line in enumerate(output):
                # 4 first header lines begin with `#`
                if i < 4:
                    self.assertEqual(line[0], "#")
                    continue

                # Following lines are regular TSV formatted lines
                pieces = line.rstrip().split("\t")

                # 5th line is a header with predefined field names
                if i == 4:
                    field_count = len(pieces)
                    field_names = pieces

                    # At least PATIENT_ID and SAMPLE_ID
                    self.assertGreaterEqual(field_count, 2)
                    self.assertIn("PATIENT_ID", pieces)
                    self.assertIn("SAMPLE_ID", pieces)
                    continue

                # TSV body: 1 row per sample
                self.assertEqual(field_count, len(pieces))
                record = dict(zip(field_names, pieces))

                self.assertTrue(REGEXP_INVALID_FOR_ID.search(record["PATIENT_ID"]) is None)
                self.assertTrue(REGEXP_INVALID_FOR_ID.search(record["SAMPLE_ID"]) is None)
                self.assertEqual(record["PATIENT_ID"], exp.sanitize_id(samples[sample_count].individual_id))
                self.assertEqual(
                    record["SAMPLE_ID"],
                    exp.sanitize_id(EXAMPLE_INGEST_PHENOPACKET["biosamples"][sample_count]["id"])
                )
                sample_count += 1

            self.assertEqual(sample_count, samples.count())

    def test_export_maf_list(self):
        exp_res = self.exp_res.filter(experiments__dataset_id=self.study_id)\
            .filter(file_format="MAF") \
            .annotate(biosample_id=F("experiments__biosample"))
        maf_count = exp_res.count()
        self.assertTrue(maf_count > 0)
        with io.StringIO() as output:
            exp.write_maf_list(exp_res, output)
            output.seek(0)
            i = 0
            for line in output:
                # line contains a drs uri
                self.assertIn("drs://", line)
                i += 1
            self.assertEqual(i, maf_count)

    def test_export_mutation_meta(self):
        with io.StringIO() as output:
            exp.mutation_meta_export(self.study_id, output)
            content = self.stream_to_dict(output)

        self.assertEqual(content["cancer_study_identifier"], self.study_id)
        self.assertEqual(content["genetic_alteration_type"], "MUTATION_EXTENDED")
        self.assertEqual(content["datatype"], "MAF")
        self.assertEqual(content["data_filename"], MUTATION_DATA_FILENAME)

    def test_export_case_list(self):
        exp_res = self.exp_res.filter(experiments__dataset_id=self.study_id)\
            .filter(file_format="MAF") \
            .annotate(biosample_id=F("experiments__biosample"))
        self.assertGreater(exp_res.count(), 0)
        with io.StringIO() as output:
            exp.case_list_export(self.study_id, exp_res, output)
            content = self.stream_to_dict(output)

        self.assertEqual(content["cancer_study_identifier"], self.study_id)
        self.assertIn(self.study_id, content["stable_id"])
        self.assertIn("case_list_name", content)
        self.assertIn("case_list_description", content)
        self.assertIn("case_list_ids", content)
        self.assertSetEqual(
            set(content["case_list_ids"].split("\t")),
            set([exp.sanitize_id(e.biosample_id) for e in exp_res])
        )


async def _agen(*items):
    for item in items:
        yield item


class CbioportalUnitTest(SimpleTestCase):
    def test_study_meta_exports_citation_when_publications_present(self):
        mock_dataset = MagicMock()
        mock_dataset.identifier = uuid.uuid4()
        mock_dataset.title = "Test Dataset"
        mock_schema = MagicMock()
        mock_schema.description = ""
        mock_schema.publications = ["doi:10.1234/test"]
        mock_dataset.to_schema.return_value = mock_schema
        with io.StringIO() as output:
            exp.study_export_meta(mock_dataset, output)
            output.seek(0)
            content = output.read()
        self.assertIn("citation", content)

    def test_sample_export_skips_null_individual_id(self):
        null_sample = MagicMock()
        null_sample.individual_id = None
        valid_sample = MagicMock()
        valid_sample.individual_id = "ind1"
        valid_sample.id = "samp1"
        valid_sample.sampled_tissue = None
        with io.StringIO() as output:
            async_to_sync(exp.sample_export)(_agen(null_sample, valid_sample), output)
            output.seek(0)
            non_header_lines = [ln for ln in output if not ln.startswith("#") and ln.strip()]
        # column header row + 1 data row (null_sample skipped)
        self.assertEqual(len(non_header_lines), 2)

    def test_sample_export_no_sampled_tissue_skips_tissue_column(self):
        sample = MagicMock()
        sample.individual_id = "ind1"
        sample.id = "samp1"
        sample.sampled_tissue = None
        with io.StringIO() as output:
            async_to_sync(exp.sample_export)(_agen(sample), output)
            output.seek(0)
            content = output.read()
        self.assertNotIn("TISSUE_LABEL", content)

    def test_make_header_generates_default_for_unmapped_field(self):
        header = CbioportalClinicalHeaderGenerator().make_header(["my_custom_field"])
        self.assertEqual(len(header), 5)
        self.assertIn("MY_CUSTOM_FIELD", header[4])

    def test_sanitize_id_replaces_invalid_chars(self):
        self.assertEqual(exp.sanitize_id("bad id!"), "bad_id_")
