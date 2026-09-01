from dateutil.parser import isoparse

from chord_metadata_service.chord.ingest import WORKFLOW_INGEST_FUNCTION_MAP
from chord_metadata_service.chord.ingest.exceptions import IngestError
from chord_metadata_service.chord.ingest.experiments import (
    validate_experiment,
    ingest_experiment,
    ingest_derived_experiment_results,
)
from chord_metadata_service.chord.ingest.schema import schema_validation, extract_error_msg
from chord_metadata_service.chord.ingest.phenopackets import (
    get_or_create_phenotypic_feature,
    get_or_create_genomic_interpretation,
    validate_phenopacket,
    ingest_phenopacket,
)
from chord_metadata_service.chord.tests.helpers import ModelFieldsTestMixin, ProjectTestCase
from chord_metadata_service.chord.workflows.metadata import (
    WORKFLOW_EXPERIMENTS_JSON,
    WORKFLOW_PHENOPACKETS_JSON,
)
from chord_metadata_service.logger import logger
from chord_metadata_service.patients.models import Individual
from chord_metadata_service.phenopackets import models as pm
from chord_metadata_service.phenopackets.schemas import PHENOPACKET_SCHEMA
from chord_metadata_service.phenopackets.tests import constants as pc
from chord_metadata_service.resources.models import Resource
from chord_metadata_service.experiments.models import Experiment, ExperimentResult, Instrument
from chord_metadata_service.experiments.schemas import EXPERIMENT_SCHEMA


from .example_ingest import (
    EXAMPLE_INGEST_MULTIPLE_PHENOPACKETS,
    EXAMPLE_INGEST_PHENOPACKET,
    EXAMPLE_INGEST_PHENOPACKET_UPDATE,
    EXAMPLE_INGEST_EXPERIMENT,
    EXAMPLE_INGEST_EXPERIMENT_BAD_BIOSAMPLE,
    EXAMPLE_INGEST_EXPERIMENT_RESULT,
    EXAMPLE_INGEST_INVALID_PHENOPACKET,
    EXAMPLE_INGEST_INVALID_EXPERIMENT,
)

IGNORE_COMMON_FIELDS = ["created", "updated", "created_by", "submitted_by"]


class IngestTest(ProjectTestCase, ModelFieldsTestMixin):

    def test_create_pf(self):
        p1 = get_or_create_phenotypic_feature({
            "description": "test",
            "type": {
                "id": "HP:0000790",
                "label": "Hematuria"
            },
            "excluded": False,
            "modifiers": [],
            "evidence": []
        })

        p2 = pm.PhenotypicFeature.objects.get(description="test")

        self.assertEqual(p1.pk, p2.pk)

        # Below is code for if we want to re-use phenotypic features in the future
        # For now, the lack of a many-to-many relationship doesn't let us do that.
        #  - David Lougheed, Nov 11 2022
        # p3 = get_or_create_phenotypic_feature({
        #     "description": "test",
        #     "type": {
        #         "id": "HP:0000790",
        #         "label": "Hematuria"
        #     },
        #     "negated": False,
        #     "modifier": [],
        #     "evidence": []
        # })
        #
        # self.assertEqual(p3.pk, p1.pk)

    # Below is code for if we want to re-use phenotypic features in the future
    # For now, the lack of a many-to-many relationship doesn't let us do that.
    #  - David Lougheed, Nov 11 2022
    # def test_create_pf_multi_existing(self):
    #     common = dict(
    #         description="test",
    #         pftype={
    #             "id": "HP:0000790",
    #             "label": "Hematuria"
    #         },
    #         negated=False,
    #         modifier=[],
    #         evidence=None,
    #         extra_properties={},
    #     )
    #
    #     p1 = PhenotypicFeature(**common)
    #     p1.save()
    #     p2 = PhenotypicFeature(**common)
    #     p2.save()
    #
    #     # skipped duplicate check, so should be different entities like Katsu used to make pre version 2.15.
    #     self.assertNotEqual(p1.pk, p2.pk)
    #
    #     common2 = {**common, "type": common["pftype"]}
    #     del common2["pftype"]
    #
    #     p3 = get_or_create_phenotypic_feature(common2)
    #
    #     # Now we get to re-use the first one
    #     self.assertEqual(p3.pk, p1.pk)

    def test_ingesting_phenopackets_json(self):
        p = WORKFLOW_INGEST_FUNCTION_MAP[WORKFLOW_PHENOPACKETS_JSON](
            EXAMPLE_INGEST_PHENOPACKET, self.dataset.identifier, logger
        )
        self.assertEqual(p.id, pm.Phenopacket.objects.get(id=p.id).id)

        # Subject
        self.assertEqual(p.subject.date_of_birth, isoparse(EXAMPLE_INGEST_PHENOPACKET["subject"]["date_of_birth"]))
        self.assert_model_fields_equal(
            db_obj=p.subject,
            ground_truth=EXAMPLE_INGEST_PHENOPACKET["subject"],
            ignore_fields=IGNORE_COMMON_FIELDS + ["date_of_birth", "vital_status"]  # DOB needs parsing
        )
        self.assertIn("__computed", EXAMPLE_INGEST_PHENOPACKET["subject"]["extra_properties"])
        self.assertNotIn("__computed", p.subject.extra_properties)  # Explicitly test computed extra_properties

        self.assert_model_fields_equal(
            db_obj=p.subject.vital_status,
            ground_truth=EXAMPLE_INGEST_PHENOPACKET["subject"]["vital_status"],
            ignore_fields=IGNORE_COMMON_FIELDS
        )

        # Phenotypic Features
        pfs = list(p.phenotypic_features.all().order_by("created"))
        self.assert_model_fields_list_equal(
            db_list=pfs,
            ground_truths=EXAMPLE_INGEST_PHENOPACKET["phenotypic_features"],
            ignore_fields=IGNORE_COMMON_FIELDS,
            field_maps={
                # JSON field mapping to model field
                "type": "pftype",
            },
        )

        # Diseases
        diseases = list(p.diseases.all().order_by("term__id"))
        self.assert_model_fields_list_equal(
            db_list=diseases,
            ground_truths=EXAMPLE_INGEST_PHENOPACKET["diseases"],
            ignore_fields=IGNORE_COMMON_FIELDS + ["id"],
        )

        # Metadata
        self.assert_model_fields_equal(
            db_obj=p.meta_data,
            ground_truth=EXAMPLE_INGEST_PHENOPACKET["meta_data"],
            ignore_fields=IGNORE_COMMON_FIELDS + ["id", "resources"]
        )

        # Metadata Resources
        resources = list(p.meta_data.resources.all().order_by("created"))
        self.assert_model_fields_list_equal(
            db_list=resources,
            ground_truths=EXAMPLE_INGEST_PHENOPACKET["meta_data"]["resources"],
            ignore_fields=IGNORE_COMMON_FIELDS
        )

        # Biosamples
        biosamples = list(p.biosamples.all().order_by("id"))
        self.assert_model_fields_list_equal(
            db_list=biosamples,
            ground_truths=EXAMPLE_INGEST_PHENOPACKET["biosamples"],
            ignore_fields=[*IGNORE_COMMON_FIELDS, "location_collected"],
        )
        self.assertEqual(
            biosamples[0].location_collected.point.coords,
            tuple(EXAMPLE_INGEST_PHENOPACKET["biosamples"][0]["location_collected"]["geometry"]["coordinates"])
        )
        self.assertEqual(
            biosamples[0].location_collected.label,
            EXAMPLE_INGEST_PHENOPACKET["biosamples"][0]["location_collected"]["properties"]["label"]
        )

        # Make sure biosamples are properly associated with phenopacket subject
        #  - Some test biosamples exclude individual_id; these should be properly associated too
        for bs in biosamples:
            self.assertEqual(bs.individual_id, p.subject.id)

        # Measurements
        self.assertEqual(p.measurements, EXAMPLE_INGEST_PHENOPACKET["measurements"])

        # Medical Actions
        self.assertEqual(p.medical_actions, EXAMPLE_INGEST_PHENOPACKET["medical_actions"])

        # Interpretations
        interpretations = list(p.interpretations.all().order_by("id"))
        self.assert_model_fields_list_equal(
            db_list=interpretations,
            ground_truths=EXAMPLE_INGEST_PHENOPACKET["interpretations"],
            ignore_fields=IGNORE_COMMON_FIELDS + ["diagnosis"],  # TODO: test diagnosis
        )

    def test_reingesting_updating_phenopackets_json(self):
        p = WORKFLOW_INGEST_FUNCTION_MAP[WORKFLOW_PHENOPACKETS_JSON](
            EXAMPLE_INGEST_PHENOPACKET, self.dataset.identifier, logger
        )
        p2 = WORKFLOW_INGEST_FUNCTION_MAP[WORKFLOW_PHENOPACKETS_JSON](
            EXAMPLE_INGEST_PHENOPACKET_UPDATE, self.dataset.identifier, logger
        )

        self.assertNotEqual(p.id, p2.id)
        self.assertEqual(p.subject.id, p2.subject.id)

        # Check that extra_properties has been replaced/augmented
        p.refresh_from_db()
        self.assertTrue(p.subject.extra_properties["music_enjoyer"])
        self.assertTrue(p2.subject.extra_properties["music_enjoyer"])
        self.assertTrue(p2.subject.extra_properties["cool_guy"])

        for b1, b2 in zip(p.biosamples.all().order_by("id"), p2.biosamples.all().order_by("id")):
            self.assertEqual(b1.id, b2.id)

        for m1, m2 in zip(p.meta_data.resources.all().order_by("id"), p2.meta_data.resources.all().order_by("id")):
            self.assertEqual(m1.id, m2.id)

        self.assert_model_fields_equal(
            p2.subject.vital_status,
            ground_truth=EXAMPLE_INGEST_PHENOPACKET_UPDATE["subject"]["vital_status"],
            ignore_fields=IGNORE_COMMON_FIELDS
        )

    def test_phenopackets_validation(self):
        # check invalid phenopacket, must fail validation & validate_phenopacket must raise

        validation = schema_validation(EXAMPLE_INGEST_INVALID_PHENOPACKET, PHENOPACKET_SCHEMA)
        self.assertEqual(validation, False)
        with self.assertRaises(IngestError):
            validate_phenopacket(EXAMPLE_INGEST_INVALID_PHENOPACKET, logger)
        with self.assertRaises(IngestError):
            ingest_phenopacket(EXAMPLE_INGEST_INVALID_PHENOPACKET, "dummy", logger, validate=True)

        # valid phenopacket passes validation & doesn't raise
        validation_2 = schema_validation(EXAMPLE_INGEST_PHENOPACKET, PHENOPACKET_SCHEMA, obj_idx=0)
        self.assertEqual(validation_2, True)
        validate_phenopacket(EXAMPLE_INGEST_PHENOPACKET, logger)

        # valid experiments pass validation
        for exp in EXAMPLE_INGEST_EXPERIMENT["experiments"]:
            validation_3 = schema_validation(exp, EXPERIMENT_SCHEMA)
            self.assertEqual(validation_3, True)

    def test_ingesting_experiments_json(self):
        # ingest phenopackets data in order to match to biosample ids
        p = WORKFLOW_INGEST_FUNCTION_MAP[WORKFLOW_PHENOPACKETS_JSON](
            EXAMPLE_INGEST_PHENOPACKET, self.dataset.identifier, logger
        )
        self.assertEqual(p.id, pm.Phenopacket.objects.get(id=p.id).id)

        # ingest list of experiments
        experiments = WORKFLOW_INGEST_FUNCTION_MAP[WORKFLOW_EXPERIMENTS_JSON](
            EXAMPLE_INGEST_EXPERIMENT, self.dataset.identifier, logger
        )

        # experiments
        self.assertEqual(len(experiments), Experiment.objects.all().count())
        self.assertEqual(experiments[0].id, EXAMPLE_INGEST_EXPERIMENT["experiments"][0]["id"])
        self.assertEqual(experiments[0].biosample.id, EXAMPLE_INGEST_EXPERIMENT["experiments"][0]["biosample"])
        self.assertEqual(experiments[0].experiment_type, EXAMPLE_INGEST_EXPERIMENT["experiments"][0]["experiment_type"])

        # experiment results
        self.assertEqual(experiments[0].experiment_results.count(), ExperimentResult.objects.all().count())

        # instrument
        self.assertEqual(Instrument.objects.all().count(), 2)

        # resources for experiments
        # - check that experiments resource is in database
        self.assertIn(EXAMPLE_INGEST_EXPERIMENT["resources"][0]["id"], [v["id"] for v in Resource.objects.values("id")])

        # try ingesting the file with an invalid biosample ID
        with self.assertRaises(pm.Biosample.DoesNotExist):
            WORKFLOW_INGEST_FUNCTION_MAP[WORKFLOW_EXPERIMENTS_JSON](
                EXAMPLE_INGEST_EXPERIMENT_BAD_BIOSAMPLE, self.dataset.identifier, logger
            )

    def test_ingesting_invalid_experiment_json(self):
        # check invalid experiment, must fail validation
        for exp in EXAMPLE_INGEST_INVALID_EXPERIMENT["experiments"]:
            validation = schema_validation(exp, EXPERIMENT_SCHEMA)
            self.assertEqual(validation, False)
            with self.assertRaises(IngestError):
                validate_experiment(exp, logger)
            with self.assertRaises(IngestError):
                ingest_experiment(exp, "dummy", logger, validate=True)

        # check valid experiment, must pass validation
        for exp in EXAMPLE_INGEST_EXPERIMENT["experiments"]:
            validation_2 = schema_validation(exp, EXPERIMENT_SCHEMA)
            self.assertEqual(validation_2, True)

    def test_ingesting_experiment_results_json(self):
        # ingest list of experiments
        WORKFLOW_INGEST_FUNCTION_MAP[WORKFLOW_PHENOPACKETS_JSON](
            EXAMPLE_INGEST_PHENOPACKET, self.dataset.identifier, logger
        )
        WORKFLOW_INGEST_FUNCTION_MAP[WORKFLOW_EXPERIMENTS_JSON](
            EXAMPLE_INGEST_EXPERIMENT, self.dataset.identifier, logger
        )
        # ingest list of experiment results
        experiment_results = ingest_derived_experiment_results(
            EXAMPLE_INGEST_EXPERIMENT_RESULT, self.dataset.identifier, logger
        )
        self.assertEqual(len(experiment_results), len(EXAMPLE_INGEST_EXPERIMENT_RESULT))
        # check that it has been linked to the same experiment as the file it
        # has been derived from.
        related_results = ExperimentResult.objects.filter(
            experiments__experiment_results__identifier=EXAMPLE_INGEST_EXPERIMENT_RESULT[0]["identifier"])
        self.assertIn(
            EXAMPLE_INGEST_EXPERIMENT_RESULT[0]["extra_properties"]["derived_from"],
            [v["identifier"] for v in related_results.values("identifier")]
        )


class SchemaHelperTest(ProjectTestCase):
    """
    Unit tests for schema validation helper functions.
    """
    def test_extract_error_msg(self):
        # mock class to simulate a jsonschema validation error
        class MockError:
            def __init__(self, message, path):
                self.message = message
                self.path = path

        # test error with nested path
        error = MockError("Invalid integer", ["body", "experiments", 0, "id"])
        msg = extract_error_msg([error])
        self.assertEqual(msg, "at field 'body -> experiments -> 0 -> id': Invalid integer")

        # test error at root
        error_root = MockError("Root object is invalid", [])
        msg_root = extract_error_msg([error_root])
        self.assertEqual(msg_root, "at field 'root': Root object is invalid")

        # test empty error list
        msg_empty = extract_error_msg([])
        self.assertEqual(msg_empty, "Unknown validation error")


class IngestMultipleTest(ProjectTestCase):
    def test_ingesting_multiple_phenopackets(self):
        ingested_phenopackets = WORKFLOW_INGEST_FUNCTION_MAP[WORKFLOW_PHENOPACKETS_JSON](
            EXAMPLE_INGEST_MULTIPLE_PHENOPACKETS, self.dataset.identifier, logger
        )
        self.assertIsInstance(ingested_phenopackets, list)
        for phenopacket in ingested_phenopackets:
            self.assertTrue(phenopacket.extra_properties["root_level"])


class IngestISOAgeToNumberTest(ProjectTestCase):

    def test_ingesting_phenopackets_json(self):
        ingested_phenopackets = WORKFLOW_INGEST_FUNCTION_MAP[WORKFLOW_PHENOPACKETS_JSON](
            EXAMPLE_INGEST_MULTIPLE_PHENOPACKETS, self.dataset.identifier, logger
        )
        self.assertIsInstance(ingested_phenopackets, list)
        # test for a single individual ind:NA20509001
        ind_1 = pm.Phenopacket.objects.get(subject="ind:NA20509001")
        self.assertIsNotNone(ind_1.subject.extra_properties)
        self.assertIsNotNone(ind_1.subject.date_of_birth)
        # test for all individuals
        for phenopacket in ingested_phenopackets:
            self.assertIsNotNone(phenopacket.subject.extra_properties)
            self.assertIsNotNone(ind_1.subject.date_of_birth)


class IngestGenomicInterpretationsTest(ProjectTestCase):

    def setUp(self):
        self.individual = Individual.objects.create(**pc.VALID_INDIVIDUAL_1)
        self.biosample = pm.Biosample.objects.create(**pc.valid_biosample_1(self.individual))
        self.biosamples = [self.biosample]

        self.base_dict = pc.valid_genomic_interpretation(
            pc.VALID_GENE_DESCRIPTOR_1, pc.valid_variant_interpretation(pc.VALID_VARIANT_DESCRIPTOR)
        )

    def test_genomic_interpretation_missing_fk_ingestion(self):
        # cannot create a genomic interpretation with a bad subject or biosample attached:
        with self.assertRaises(IngestError):
            get_or_create_genomic_interpretation(
                {**self.base_dict, "subject_or_biosample_id": ""},
                self.individual,
                self.biosamples,
            )

    def test_genomic_interpretation_biosample_ingestion(self):
        gi = get_or_create_genomic_interpretation(
            {**self.base_dict, "subject_or_biosample_id": str(self.biosample.id)},
            self.individual,
            self.biosamples,
        )

        self.assertEqual(gi.biosample, self.biosample)
        self.assertIsNone(gi.subject)

        # same thing again, should reuse
        gi2 = get_or_create_genomic_interpretation(
            {**self.base_dict, "subject_or_biosample_id": str(self.biosample.id)},
            self.individual,
            self.biosamples,
        )

        self.assertEqual(gi2.biosample, self.biosample)
        self.assertIsNone(gi2.subject)

        # should have same ID due to re-use:
        self.assertEqual(gi.pk, gi2.pk)

    def test_genomic_interpretation_subject_ingestion(self):
        gi = get_or_create_genomic_interpretation(
            {**self.base_dict, "subject_or_biosample_id": str(self.individual.id)},
            self.individual,
            self.biosamples,
        )

        self.assertEqual(gi.subject, self.individual)
        self.assertIsNone(gi.biosample)

        # same thing again, should reuse
        gi2 = get_or_create_genomic_interpretation(
            {**self.base_dict, "subject_or_biosample_id": str(self.individual.id)},
            self.individual,
            self.biosamples,
        )

        self.assertEqual(gi2.subject, self.individual)
        self.assertIsNone(gi2.biosample)

        # should have same ID due to re-use:
        self.assertEqual(gi.pk, gi2.pk)

    def test_genomic_interpretation_reuse_behaviour(self):
        gi = get_or_create_genomic_interpretation(
            {**self.base_dict, "subject_or_biosample_id": str(self.biosample.id)},
            self.individual,
            self.biosamples,
        )
        self.assertEqual(gi.biosample, self.biosample)
        self.assertIsNone(gi.subject)

        # different because it uses an individual ID instead
        gi2 = get_or_create_genomic_interpretation(
            {**self.base_dict, "subject_or_biosample_id": str(self.individual.id)},
            self.individual,
            self.biosamples,
        )
        self.assertEqual(gi2.subject, self.individual)
        self.assertIsNone(gi2.biosample)

        # ... and thus have different primary keys:
        self.assertNotEqual(gi.pk, gi2.pk)

    def test_genomic_interpretation_same_id_error(self):
        ind = Individual.objects.create(**{**pc.VALID_INDIVIDUAL_1, "id": "same-id"})
        bio = pm.Biosample.objects.create(**{**pc.valid_biosample_1(self.individual), "id": "same-id"})

        with self.assertRaises(IngestError):
            get_or_create_genomic_interpretation({**self.base_dict, "subject_or_biosample_id": "same-id"}, ind, [bio])
