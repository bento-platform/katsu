from django.test import TestCase
from chord_metadata_service.chord.ingest.views import DATASET_ID_OVERRIDES
from dateutil.parser import isoparse

from chord_metadata_service.chord.models import Project, Dataset
from chord_metadata_service.chord.ingest import WORKFLOW_INGEST_FUNCTION_MAP
from chord_metadata_service.chord.ingest.exceptions import IngestError
from chord_metadata_service.chord.ingest.experiments import (
    validate_experiment,
    ingest_experiment,
)
from chord_metadata_service.chord.ingest.schema import schema_validation
from chord_metadata_service.chord.ingest.phenopackets import (
    get_or_create_phenotypic_feature,
    validate_phenopacket,
    ingest_phenopacket,
)
from chord_metadata_service.chord.workflows.metadata import (
    WORKFLOW_EXPERIMENTS_JSON,
    WORKFLOW_MAF_DERIVED_FROM_VCF_JSON,
    WORKFLOW_PHENOPACKETS_JSON,
)
from chord_metadata_service.phenopackets.models import Biosample, PhenotypicFeature, Phenopacket
from chord_metadata_service.phenopackets.schemas import PHENOPACKET_SCHEMA
from chord_metadata_service.resources.models import Resource
from chord_metadata_service.experiments.models import Experiment, ExperimentResult, Instrument
from chord_metadata_service.experiments.schemas import EXPERIMENT_SCHEMA


from .constants import VALID_DATA_USE_1
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


class IngestTest(TestCase):
    def setUp(self) -> None:
        p = Project.objects.create(title="Project 1", description="")
        self.d = Dataset.objects.create(title="Dataset 1", description="Some dataset", data_use=VALID_DATA_USE_1,
                                        project=p)

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

        p2 = PhenotypicFeature.objects.get(description="test")

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
        p = WORKFLOW_INGEST_FUNCTION_MAP[WORKFLOW_PHENOPACKETS_JSON](EXAMPLE_INGEST_PHENOPACKET, self.d.identifier)
        self.assertEqual(p.id, Phenopacket.objects.get(id=p.id).id)

        self.assertEqual(p.subject.id, EXAMPLE_INGEST_PHENOPACKET["subject"]["id"])
        self.assertEqual(p.subject.date_of_birth, isoparse(EXAMPLE_INGEST_PHENOPACKET["subject"]["date_of_birth"]))
        self.assertEqual(p.subject.sex, EXAMPLE_INGEST_PHENOPACKET["subject"]["sex"])
        self.assertEqual(p.subject.karyotypic_sex, EXAMPLE_INGEST_PHENOPACKET["subject"]["karyotypic_sex"])

        self.assertIn("__computed", EXAMPLE_INGEST_PHENOPACKET["subject"]["extra_properties"])
        self.assertNotIn("__computed", p.subject.extra_properties)

        pfs = list(p.phenotypic_features.all().order_by("pftype__id"))

        self.assertEqual(len(pfs), 2)
        self.assertEqual(pfs[0].description, EXAMPLE_INGEST_PHENOPACKET["phenotypic_features"][0]["description"])
        self.assertEqual(pfs[0].pftype["id"], EXAMPLE_INGEST_PHENOPACKET["phenotypic_features"][0]["type"]["id"])
        self.assertEqual(pfs[0].pftype["label"], EXAMPLE_INGEST_PHENOPACKET["phenotypic_features"][0]["type"]["label"])
        self.assertEqual(pfs[0].excluded, EXAMPLE_INGEST_PHENOPACKET["phenotypic_features"][0]["excluded"])
        # TODO: Test more properties

        diseases = list(p.diseases.all().order_by("term__id"))
        self.assertEqual(len(diseases), 1)
        for field in ["term", "excluded", "onset", "resolution", "disease_stage",
                      "clinical_tnm_finding", "primary_site", "laterality"]:
            self.assertEqual(getattr(diseases[0], field), EXAMPLE_INGEST_PHENOPACKET["diseases"][0][field])

        # TODO: Test Metadata

        biosamples = list(p.biosamples.all().order_by("id"))
        self.assertEqual(len(biosamples), 5)

        # Make sure biosamples are properly associated with phenopacket subject
        #  - Some test biosamples exclude individual_id; these should be properly associated too
        for bs in biosamples:
            self.assertEqual(bs.individual_id, p.subject.id)

        # TODO: More

    def test_reingesting_updating_phenopackets_json(self):
        p = WORKFLOW_INGEST_FUNCTION_MAP[WORKFLOW_PHENOPACKETS_JSON](EXAMPLE_INGEST_PHENOPACKET, self.d.identifier)
        p2 = WORKFLOW_INGEST_FUNCTION_MAP[WORKFLOW_PHENOPACKETS_JSON](EXAMPLE_INGEST_PHENOPACKET_UPDATE,
                                                                      self.d.identifier)

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

    def test_phenopackets_validation(self):
        # check invalid phenopacket, must fail validation & validate_phenopacket must raise

        validation = schema_validation(EXAMPLE_INGEST_INVALID_PHENOPACKET, PHENOPACKET_SCHEMA)
        self.assertEqual(validation, False)
        with self.assertRaises(IngestError):
            validate_phenopacket(EXAMPLE_INGEST_INVALID_PHENOPACKET)
        with self.assertRaises(IngestError):
            ingest_phenopacket(EXAMPLE_INGEST_INVALID_PHENOPACKET, "dummy", validate=True)

        # valid phenopacket passes validation & doesn't raise
        validation_2 = schema_validation(EXAMPLE_INGEST_PHENOPACKET, PHENOPACKET_SCHEMA)
        self.assertEqual(validation_2, True)
        validate_phenopacket(EXAMPLE_INGEST_PHENOPACKET)

        # valid experiments pass validation
        for exp in EXAMPLE_INGEST_EXPERIMENT["experiments"]:
            validation_3 = schema_validation(exp, EXPERIMENT_SCHEMA)
            self.assertEqual(validation_3, True)

    def test_ingesting_experiments_json(self):
        # ingest phenopackets data in order to match to biosample ids
        p = WORKFLOW_INGEST_FUNCTION_MAP[WORKFLOW_PHENOPACKETS_JSON](EXAMPLE_INGEST_PHENOPACKET, self.d.identifier)
        self.assertEqual(p.id, Phenopacket.objects.get(id=p.id).id)

        # ingest list of experiments
        experiments = WORKFLOW_INGEST_FUNCTION_MAP[WORKFLOW_EXPERIMENTS_JSON](
            EXAMPLE_INGEST_EXPERIMENT, self.d.identifier
        )

        # experiments
        self.assertEqual(len(experiments), Experiment.objects.all().count())
        self.assertEqual(experiments[0].id, EXAMPLE_INGEST_EXPERIMENT["experiments"][0]["id"])
        self.assertEqual(experiments[0].biosample.id, EXAMPLE_INGEST_EXPERIMENT["experiments"][0]["biosample"])
        self.assertEqual(experiments[0].experiment_type, EXAMPLE_INGEST_EXPERIMENT["experiments"][0]["experiment_type"])

        # experiment results
        self.assertEqual(experiments[0].experiment_results.count(), ExperimentResult.objects.all().count())

        # instrument
        self.assertEqual(Instrument.objects.all().count(), 1)

        # resources for experiments
        # - check that experiments resource is in database
        self.assertIn(EXAMPLE_INGEST_EXPERIMENT["resources"][0]["id"], [v["id"] for v in Resource.objects.values("id")])

        # try ingesting the file with an invalid biosample ID
        with self.assertRaises(Biosample.DoesNotExist):
            WORKFLOW_INGEST_FUNCTION_MAP[WORKFLOW_EXPERIMENTS_JSON](
                EXAMPLE_INGEST_EXPERIMENT_BAD_BIOSAMPLE, self.d.identifier
            )

    def test_ingesting_invalid_experiment_json(self):
        # check invalid experiment, must fail validation
        for exp in EXAMPLE_INGEST_INVALID_EXPERIMENT["experiments"]:
            validation = schema_validation(exp, EXPERIMENT_SCHEMA)
            self.assertEqual(validation, False)
            with self.assertRaises(IngestError):
                validate_experiment(exp)
            with self.assertRaises(IngestError):
                ingest_experiment(exp, "dummy", validate=True)

        # check valid experiment, must pass validation
        for exp in EXAMPLE_INGEST_EXPERIMENT["experiments"]:
            validation_2 = schema_validation(exp, EXPERIMENT_SCHEMA)
            self.assertEqual(validation_2, True)

    def test_ingesting_experiment_results_json(self):
        # ingest list of experiments
        WORKFLOW_INGEST_FUNCTION_MAP[WORKFLOW_PHENOPACKETS_JSON](EXAMPLE_INGEST_PHENOPACKET, self.d.identifier)
        WORKFLOW_INGEST_FUNCTION_MAP[WORKFLOW_EXPERIMENTS_JSON](
            EXAMPLE_INGEST_EXPERIMENT, self.d.identifier
        )
        # ingest list of experiment results
        experiment_results = WORKFLOW_INGEST_FUNCTION_MAP[WORKFLOW_MAF_DERIVED_FROM_VCF_JSON](
            EXAMPLE_INGEST_EXPERIMENT_RESULT, DATASET_ID_OVERRIDES
        )
        self.assertEqual(len(experiment_results), len(EXAMPLE_INGEST_EXPERIMENT_RESULT))
        # check that it has been linked to the same experiment as the file it
        # has been derived from.
        related_results = ExperimentResult.objects.filter(
            experiment__experiment_results__identifier=EXAMPLE_INGEST_EXPERIMENT_RESULT[0]["identifier"])
        self.assertIn(
            EXAMPLE_INGEST_EXPERIMENT_RESULT[0]["extra_properties"]["derived_from"],
            [v["identifier"] for v in related_results.values("identifier")]
        )


class IngestISOAgeToNumberTest(TestCase):
    def setUp(self) -> None:
        p = Project.objects.create(title="Project 1", description="")
        self.d = Dataset.objects.create(title="Dataset 1", description="Some dataset", data_use=VALID_DATA_USE_1,
                                        project=p)

    def test_ingesting_phenopackets_json(self):
        ingested_phenopackets = WORKFLOW_INGEST_FUNCTION_MAP[WORKFLOW_PHENOPACKETS_JSON](
            EXAMPLE_INGEST_MULTIPLE_PHENOPACKETS, self.d.identifier
        )
        self.assertIsInstance(ingested_phenopackets, list)
        # test for a single individual ind:NA20509001
        ind_1 = Phenopacket.objects.get(subject="ind:NA20509001")
        self.assertIsNotNone(ind_1.subject.extra_properties)
        self.assertIsNotNone(ind_1.subject.date_of_birth)
        # test for all individuals
        for phenopacket in ingested_phenopackets:
            self.assertIsNotNone(phenopacket.subject.extra_properties)
            self.assertIsNotNone(ind_1.subject.date_of_birth)
