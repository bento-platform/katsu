import io
from typing import TextIO
from os import walk, path

from django.db.models import F
from django.test import TestCase

from chord_metadata_service.chord.export import cbioportal as exp
from chord_metadata_service.chord.export.cbioportal import (
    CBIO_FILES_SET,
    MUTATION_DATA_FILENAME,
    PATIENT_DATA_FILENAME,
    PATIENT_DATATYPE,
    REGEXP_INVALID_FOR_ID,
    SAMPLE_DATA_FILENAME,
    SAMPLE_DATATYPE,
)
from chord_metadata_service.chord.export.utils import ExportFileContext
from chord_metadata_service.chord.models import Project, Dataset
from chord_metadata_service.experiments.models import ExperimentResult
from chord_metadata_service.chord.ingest import WORKFLOW_INGEST_FUNCTION_MAP
from chord_metadata_service.chord.ingest.experiments import ingest_derived_experiment_results
from chord_metadata_service.chord.workflows.metadata import (
    WORKFLOW_EXPERIMENTS_JSON,
    WORKFLOW_PHENOPACKETS_JSON,
)
from chord_metadata_service.patients.models import Individual
from chord_metadata_service.phenopackets import models as pm


from .constants import VALID_DATA_USE_1
from .example_ingest import (
    EXAMPLE_INGEST_EXPERIMENT,
    EXAMPLE_INGEST_EXPERIMENT_RESULT,
    EXAMPLE_INGEST_PHENOPACKET,
)


class ExportCBioTest(TestCase):
    def setUp(self) -> None:
        # Creates a test database and populate with a phenopacket test file

        p = Project.objects.create(title="Project 1", description="")
        self.d = Dataset.objects.create(title="Dataset 1", description="Some dataset", data_use=VALID_DATA_USE_1,
                                        project=p)
        self.study_id = str(self.d.identifier)

        self.p = WORKFLOW_INGEST_FUNCTION_MAP[WORKFLOW_PHENOPACKETS_JSON](EXAMPLE_INGEST_PHENOPACKET, self.d.identifier)
        # ingest list of experiments
        self.exp = WORKFLOW_INGEST_FUNCTION_MAP[WORKFLOW_EXPERIMENTS_JSON](
            EXAMPLE_INGEST_EXPERIMENT, self.d.identifier
        )
        # append derived MAF files to experiment results
        ingest_derived_experiment_results(EXAMPLE_INGEST_EXPERIMENT_RESULT, self.d.identifier)
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
            exp.study_export(file_export.get_path, self.study_id)
            export_dir = file_export.get_path()
            self.assertTrue(path.exists(export_dir))

            # recursively walk the export dir to get the generated files
            files_set = set()
            for dirpath, dirnames, filenames in walk(export_dir):
                files_set.update([path.relpath(path.join(dirpath, fn), export_dir) for fn in filenames])

            self.assertTrue(CBIO_FILES_SET.issubset(files_set))

    def test_export_cbio_study_meta(self):
        with io.StringIO() as output:
            exp.study_export_meta(self.d, output)
            content = self.stream_to_dict(output)

        self.assertIn("type_of_cancer", content)
        self.assertEqual(content["cancer_study_identifier"], self.study_id)
        self.assertEqual(content["name"], self.d.title)
        self.assertEqual(content["description"], self.d.description)

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
            exp.individual_export(indiv, output)
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
        samples = pm.Biosample.objects.filter(phenopacket=self.p)

        with io.StringIO() as output:
            exp.sample_export(samples, output)
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
        exp_res = self.exp_res.filter(experiment__dataset_id=self.study_id)\
            .filter(file_format="MAF") \
            .annotate(biosample_id=F("experiment__biosample"))
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
        exp_res = self.exp_res.filter(experiment__dataset_id=self.study_id)\
            .filter(file_format="MAF") \
            .annotate(biosample_id=F("experiment__biosample"))
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
