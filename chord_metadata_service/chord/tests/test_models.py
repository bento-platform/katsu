from django.db.utils import IntegrityError
from django.test import TestCase
from django.core.exceptions import ValidationError
from uuid import uuid4
from bento_lib.discovery import DiscoveryConfig
from chord_metadata_service.chord.dataset_schema import KatsuDatasetModel
from chord_metadata_service.chord.tests.helpers import ProjectTestCase

from chord_metadata_service.patients.models import Individual
from chord_metadata_service.phenopackets.models import Biosample, MetaData, Phenopacket
from chord_metadata_service.phenopackets.tests.constants import (
    valid_biosample_1,
    VALID_INDIVIDUAL_1
)
from chord_metadata_service.restapi.models import SchemaType
from ..models import Project, ProjectJsonSchema, DatasetV2, DatasetV2Translation
from .constants import VALID_DATASET_V2_PRIMARY_CONTACT


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
        self.assertEqual(str(p2), f"Project 2 (ID: {str(p2.identifier)})")

    def test_project_discovery_null(self):
        p = Project.objects.get(title="Project 1")
        self.assertIsNone(p.discovery)

    def test_project_discovery_config(self):
        cfg = DiscoveryConfig()
        p = Project.objects.create(title="Project 3", description="", discovery=cfg)
        reloaded = Project.objects.get(pk=p.pk)
        self.assertIsInstance(reloaded.discovery, DiscoveryConfig)


TABLE_ID = str(uuid4())
SERVICE_ID = str(uuid4())


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
        biosample = Biosample.objects.create(**valid_biosample_1(individual))
        meta_data = MetaData.objects.create(
            created_by="test",
            submitted_by="test"
        )
        phenopacket = Phenopacket.objects.create(
            id="phenopacket_id:1",
            subject=individual,
            dataset=self.dataset_v2,
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


class DatasetV2Test(ProjectTestCase):
    def test_str(self):
        self.assertEqual(str(self.dataset_v2), f"{self.dataset_v2.identifier}: {self.dataset_v2.title}")

    def test_resources_empty(self):
        self.assertEqual(self.dataset_v2.resources.count(), 0)

    def test_to_schema(self):
        schema = self.dataset_v2.to_schema()
        self.assertIsInstance(schema, KatsuDatasetModel)
        self.assertEqual(schema.title, self.dataset_v2.title)

    def test_update_from_schema(self):
        new_title = "Updated Title"
        updated_schema = KatsuDatasetModel(
            schema_version="1.0",
            title=new_title,
            description="Updated description",
            primary_contact=VALID_DATASET_V2_PRIMARY_CONTACT,
            identifier=str(self.dataset_v2.identifier),
            project=str(self.project.identifier),
        )
        dv2 = DatasetV2.objects.get(pk=self.dataset_v2.identifier)
        dv2.update_from_schema(updated_schema)
        dv2.save()
        reloaded = DatasetV2.objects.get(pk=self.dataset_v2.identifier)
        self.assertEqual(reloaded.title, new_title)


class DatasetV2TranslationTest(ProjectTestCase):
    def setUp(self):
        schema = KatsuDatasetModel(
            schema_version="1.0",
            title="Dataset V2 Translation Test",
            description="Test translation",
            primary_contact=VALID_DATASET_V2_PRIMARY_CONTACT,
            identifier=str(self.dataset_v2.identifier),
            project=str(self.project.identifier),
        )
        self.translation = DatasetV2Translation.from_schema(
            schema, dataset_id=self.dataset_v2.identifier, language='fr'
        )
        self.translation.save()

    def test_str(self):
        self.assertEqual(str(self.translation), f"{self.dataset_v2.identifier}: fr")

    def test_unique_together(self):
        dup = DatasetV2Translation(
            dataset=self.dataset_v2,
            language='fr',
            data=self.translation.data,
        )
        with self.assertRaises(IntegrityError):
            dup.save()

    def test_translation_data_stored(self):
        reloaded = DatasetV2Translation.objects.get(pk=self.translation.pk)
        self.assertEqual(reloaded.language, 'fr')
        self.assertEqual(reloaded.dataset_id, self.dataset_v2.identifier)
