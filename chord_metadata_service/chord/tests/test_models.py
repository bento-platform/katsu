from django.db.utils import IntegrityError
from django.test import TestCase
from django.core.exceptions import ValidationError
from uuid import uuid4
from chord_metadata_service.chord.tests.helpers import ProjectTestCase

from chord_metadata_service.patients.models import Individual
from chord_metadata_service.phenopackets.models import Biosample, MetaData, Phenopacket, Procedure
from chord_metadata_service.phenopackets.tests.constants import (
    valid_biosample_1,
    VALID_PROCEDURE_1,
    VALID_INDIVIDUAL_1
)
from chord_metadata_service.restapi.models import SchemaType
from ..data_types import DATA_TYPE_PHENOPACKET
from ..models import Project, Dataset, ProjectJsonSchema, TableOwnership, Table
from .constants import VALID_DATA_USE_1


P2_DESC = "This is a good project..."


class ProjectTest(TestCase):
    def setUp(self) -> None:
        Project.objects.create(title="Project 1", description="")
        Project.objects.create(title="Project 2", description=P2_DESC)

    def test_project(self):
        p1 = Project.objects.get(title="Project 1")
        p2 = Project.objects.get(title="Project 2")

        self.assertEqual(p1.description, "")
        self.assertEqual(p2.description, P2_DESC)

        self.assertEqual(str(p1), f"Project 1 (ID: {str(p1.identifier)})")


class DatasetTest(TestCase):
    def setUp(self) -> None:
        p = Project.objects.create(title="Project 1", description="")
        Dataset.objects.create(title="Dataset 1", description="Some dataset", data_use=VALID_DATA_USE_1, project=p)

    def test_dataset(self):
        p = Project.objects.get(title="Project 1")
        d = Dataset.objects.get(title="Dataset 1")

        self.assertEqual(d.description, "Some dataset")
        self.assertDictEqual(d.data_use, VALID_DATA_USE_1)
        self.assertEqual(d.project, p)

        self.assertEqual(str(d), f"Dataset 1 (ID: {str(d.identifier)})")

        self.assertIn(d.identifier, set(d2.identifier for d2 in p.datasets.all()))


TABLE_ID = str(uuid4())
SERVICE_ID = str(uuid4())


class TableOwnershipTest(TestCase):
    def setUp(self) -> None:
        p = Project.objects.create(title="Project 1", description="")
        d = Dataset.objects.create(title="Dataset 1", description="", data_use=VALID_DATA_USE_1, project=p)
        TableOwnership.objects.create(
            table_id=TABLE_ID,
            service_id=SERVICE_ID,
            service_artifact="variant",
            dataset=d
        )

    def test_table_ownership(self):
        d = Dataset.objects.get(title="Dataset 1")
        t = TableOwnership.objects.get(table_id=TABLE_ID, service_id=SERVICE_ID)

        self.assertEqual(t.service_artifact, "variant")
        self.assertEqual(t.dataset, d)

        self.assertIn(t, d.table_ownership.all())

        self.assertEqual(str(t), f"{str(d)} -> {t.table_id}")


class TableTest(TestCase):
    def setUp(self) -> None:
        p = Project.objects.create(title="Project 1", description="")
        self.d = Dataset.objects.create(title="Dataset 1", description="", data_use=VALID_DATA_USE_1, project=p)
        to = TableOwnership.objects.create(
            table_id=TABLE_ID,
            service_id=SERVICE_ID,
            service_artifact="variant",
            dataset=self.d
        )
        Table.objects.create(ownership_record=to, name="Table 1", data_type=DATA_TYPE_PHENOPACKET)

    def test_table(self):
        t = Table.objects.get(ownership_record_id=TABLE_ID)

        self.assertEqual(t.data_type, DATA_TYPE_PHENOPACKET)
        self.assertEqual(t.identifier, TABLE_ID)
        self.assertEqual(t.dataset, self.d)

        self.assertEqual(str(t), f"{t.name} (ID: {TABLE_ID}, Type: {DATA_TYPE_PHENOPACKET})")


class ProjectJsonSchemaTest(ProjectTestCase):
    def setUp(self) -> None:
        self.json_schema = {
            "type": "object",
            "properties": {
                "prop_a": {"type": "string"}
            },
            "required": ["prop_a"]
        }
        self.required_pheno_schema = ProjectJsonSchema.objects.create(
            project=self.project,
            required=True,
            json_schema=self.json_schema,
            schema_type=SchemaType.PHENOPACKET
        )

    def test_project_json_schema(self):
        proj_json_schema = ProjectJsonSchema.objects.get(id=self.required_pheno_schema.id)
        self.assertEqual(proj_json_schema.project_id, self.project.identifier)
        self.assertEqual(proj_json_schema.json_schema, self.json_schema)
        self.assertEqual(proj_json_schema.schema_type, SchemaType.PHENOPACKET)

    def test_schema_type_constraint(self):
        # ProjectJsonSchema must be unique for every project_id, schema_type pair
        # Should fail
        invalid_pjs = ProjectJsonSchema(
            project=self.project,
            required=False,
            json_schema={"type": "string"},
            schema_type=SchemaType.PHENOPACKET
        )
        with self.assertRaises(IntegrityError):
            # Should fail;
            invalid_pjs.save()

    def test_existing_data_validation(self):
        # Add a Phenopacket with an Individual and a Biosample to the project
        individual = Individual.objects.create(**VALID_INDIVIDUAL_1)
        procedure = Procedure.objects.create(**VALID_PROCEDURE_1)
        biosample = Biosample.objects.create(**valid_biosample_1(individual, procedure))
        meta_data = MetaData.objects.create(
            created_by="test",
            submitted_by="test"
        )
        phenopacket = Phenopacket.objects.create(
            id="phenopacket_id:1",
            subject=individual,
            table=self.table,
            extra_properties={
                "prop_a": "extra property text"
            },
            meta_data=meta_data,
        )
        phenopacket.biosamples.set([biosample])

        # Tentative new ProjectJsonSchema for Individual
        invalid_pjs_individual = ProjectJsonSchema(
            project=self.project,
            required=False,
            json_schema={"type": "string"},
            schema_type=SchemaType.INDIVIDUAL
        )
        # Tentative new ProjectJsonSchema for Biosample
        invalid_pjs_biosample = ProjectJsonSchema(
            project=self.project,
            required=False,
            json_schema={"type": "string"},
            schema_type=SchemaType.BIOSAMPLE
        )

        with self.assertRaises(ValidationError):
            # An individual exists already for this project
            invalid_pjs_individual.save()
        with self.assertRaises(ValidationError):
            # A biosample exists already for this project
            invalid_pjs_biosample.save()
