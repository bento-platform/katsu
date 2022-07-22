import uuid

from django.test import TestCase
from dateutil.parser import isoparse

from chord_metadata_service.chord.data_types import DATA_TYPE_PHENOPACKET, DATA_TYPE_EXPERIMENT
from chord_metadata_service.chord.models import Project, Dataset, TableOwnership, Table
# noinspection PyProtectedMember
from chord_metadata_service.chord.ingest import (
    WORKFLOW_PHENOPACKETS_JSON,
    create_phenotypic_feature,
    WORKFLOW_INGEST_FUNCTION_MAP,
    WORKFLOW_EXPERIMENTS_JSON,
    schema_validation
)
from chord_metadata_service.phenopackets.models import PhenotypicFeature, Phenopacket
from chord_metadata_service.phenopackets.schemas import PHENOPACKET_SCHEMA
from chord_metadata_service.resources.models import Resource
from chord_metadata_service.experiments.models import Experiment, ExperimentResult, Instrument
from chord_metadata_service.experiments.schemas import EXPERIMENT_SCHEMA
from chord_metadata_service.restapi.utils import iso_duration_to_years


from .constants import VALID_DATA_USE_1
from .example_ingest import (
    EXAMPLE_INGEST_PHENOPACKET,
    EXAMPLE_INGEST_OUTPUTS,
    EXAMPLE_INGEST_EXPERIMENT,
    EXAMPLE_INGEST_OUTPUTS_EXPERIMENT,
    EXAMPLE_INGEST_INVALID_PHENOPACKET,
    EXAMPLE_INGEST_MULTIPLE_OUTPUTS,
    EXAMPLE_INGEST_INVALID_EXPERIMENT,
)


class IngestTest(TestCase):
    def setUp(self) -> None:
        p = Project.objects.create(title="Project 1", description="")
        self.d = Dataset.objects.create(title="Dataset 1", description="Some dataset", data_use=VALID_DATA_USE_1,
                                        project=p)
        # TODO: Real service ID
        # table for phenopackets
        to = TableOwnership.objects.create(table_id=uuid.uuid4(), service_id=uuid.uuid4(), service_artifact="metadata",
                                           dataset=self.d)
        self.t = Table.objects.create(ownership_record=to, name="Table 1", data_type=DATA_TYPE_PHENOPACKET)

        # table for experiments metadata
        to_exp = TableOwnership.objects.create(table_id=uuid.uuid4(), service_id=uuid.uuid4(),
                                               service_artifact="experiments", dataset=self.d)
        self.t_exp = Table.objects.create(ownership_record=to_exp, name="Table 2", data_type=DATA_TYPE_EXPERIMENT)

    def test_create_pf(self):
        p1 = create_phenotypic_feature({
            "description": "test",
            "type": {
                "id": "HP:0000790",
                "label": "Hematuria"
            },
            "negated": False,
            "modifier": [],
            "evidence": []
        })

        p2 = PhenotypicFeature.objects.get(description="test")

        self.assertEqual(p1.pk, p2.pk)

    def test_ingesting_phenopackets_json(self):
        p = WORKFLOW_INGEST_FUNCTION_MAP[WORKFLOW_PHENOPACKETS_JSON](EXAMPLE_INGEST_OUTPUTS, self.t.identifier)
        self.assertEqual(p.id, Phenopacket.objects.get(id=p.id).id)

        self.assertEqual(p.subject.id, EXAMPLE_INGEST_PHENOPACKET["subject"]["id"])
        self.assertEqual(p.subject.date_of_birth, isoparse(EXAMPLE_INGEST_PHENOPACKET["subject"]["date_of_birth"]))
        self.assertEqual(p.subject.sex, EXAMPLE_INGEST_PHENOPACKET["subject"]["sex"])
        self.assertEqual(p.subject.karyotypic_sex, EXAMPLE_INGEST_PHENOPACKET["subject"]["karyotypic_sex"])

        pfs = list(p.phenotypic_features.all().order_by("pftype__id"))

        self.assertEqual(len(pfs), 2)
        self.assertEqual(pfs[0].description, EXAMPLE_INGEST_PHENOPACKET["phenotypic_features"][0]["description"])
        self.assertEqual(pfs[0].pftype["id"], EXAMPLE_INGEST_PHENOPACKET["phenotypic_features"][0]["type"]["id"])
        self.assertEqual(pfs[0].pftype["label"], EXAMPLE_INGEST_PHENOPACKET["phenotypic_features"][0]["type"]["label"])
        self.assertEqual(pfs[0].negated, EXAMPLE_INGEST_PHENOPACKET["phenotypic_features"][0]["negated"])
        # TODO: Test more properties

        diseases = list(p.diseases.all().order_by("term__id"))
        self.assertEqual(len(diseases), 1)
        # TODO: More

        # TODO: Test Metadata

        biosamples = list(p.biosamples.all().order_by("id"))
        self.assertEqual(len(biosamples), 5)
        # TODO: More

        # Test ingesting again
        p2 = WORKFLOW_INGEST_FUNCTION_MAP[WORKFLOW_PHENOPACKETS_JSON](EXAMPLE_INGEST_OUTPUTS, self.t.identifier)
        self.assertNotEqual(p.id, p2.id)
        # TODO: More

    def test_ingesting_invalid_phenopackets_json(self):
        # check invalid phenopacket, must fail validation
        validation = schema_validation(EXAMPLE_INGEST_INVALID_PHENOPACKET, PHENOPACKET_SCHEMA)
        self.assertEqual(validation, False)
        # valid phenopacket passes validation
        validation_2 = schema_validation(EXAMPLE_INGEST_PHENOPACKET, PHENOPACKET_SCHEMA)
        self.assertEqual(validation_2, True)
        # valid experiments pass validation
        for exp in EXAMPLE_INGEST_EXPERIMENT["experiments"]:
            validation_3 = schema_validation(exp, EXPERIMENT_SCHEMA)
            self.assertEqual(validation_3, True)

    def test_ingesting_experiments_json(self):
        # ingest phenopackets data in order to match to biosample ids
        p = WORKFLOW_INGEST_FUNCTION_MAP[WORKFLOW_PHENOPACKETS_JSON](EXAMPLE_INGEST_OUTPUTS, self.t.identifier)
        self.assertEqual(p.id, Phenopacket.objects.get(id=p.id).id)
        # ingest list of experiments
        experiments = WORKFLOW_INGEST_FUNCTION_MAP[WORKFLOW_EXPERIMENTS_JSON](
            EXAMPLE_INGEST_OUTPUTS_EXPERIMENT, self.t_exp.identifier
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
        # check that experiments resource is in database
        self.assertIn(EXAMPLE_INGEST_EXPERIMENT["resources"][0]["id"], [v["id"] for v in Resource.objects.values("id")])

    def test_ingesting_invalid_experiment_json(self):
        # check invalid experiment, must fail validation
        for exp in EXAMPLE_INGEST_INVALID_EXPERIMENT["experiments"]:
            validation = schema_validation(exp, EXPERIMENT_SCHEMA)
            self.assertEqual(validation, False)
        # check valid experiment, must pass validation
        for exp in EXAMPLE_INGEST_EXPERIMENT["experiments"]:
            validation_2 = schema_validation(exp, EXPERIMENT_SCHEMA)
            self.assertEqual(validation_2, True)


class IngestISOAgeToNumberTest(TestCase):
    def setUp(self) -> None:
        p = Project.objects.create(title="Project 1", description="")
        self.d = Dataset.objects.create(title="Dataset 1", description="Some dataset", data_use=VALID_DATA_USE_1,
                                        project=p)
        # table for phenopackets
        to = TableOwnership.objects.create(table_id=uuid.uuid4(), service_id=uuid.uuid4(), service_artifact="metadata",
                                           dataset=self.d)
        self.t = Table.objects.create(ownership_record=to, name="Table 1", data_type=DATA_TYPE_PHENOPACKET)

    def test_ingesting_phenopackets_json(self):
        ingested_phenopackets = WORKFLOW_INGEST_FUNCTION_MAP[WORKFLOW_PHENOPACKETS_JSON](
            EXAMPLE_INGEST_MULTIPLE_OUTPUTS, self.t.identifier
        )
        self.assertIsInstance(ingested_phenopackets, list)
        # test for a single individual ind:NA20509001
        ind_1 = Phenopacket.objects.get(subject="ind:NA20509001")
        self.assertIsNotNone(ind_1.subject.age_numeric)
        self.assertIsNotNone(ind_1.subject.age_unit)
        # test for all individuals
        for phenopacket in ingested_phenopackets:
            if phenopacket.subject.age:
                if "age" in phenopacket.subject.age:
                    self.assertIsNotNone(phenopacket.subject.age_numeric)
                    self.assertEqual(
                        iso_duration_to_years(phenopacket.subject.age["age"])[0],
                        phenopacket.subject.age_numeric
                    )
                    self.assertIsNotNone(phenopacket.subject.age_unit)
                # if age range then age_numeric is None
                else:
                    self.assertIsNone(phenopacket.subject.age_numeric)
            # if no age then no age_numeric
            else:
                self.assertIsNone(phenopacket.subject.age_numeric)
