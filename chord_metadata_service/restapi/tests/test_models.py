from django.core.exceptions import ValidationError
from chord_metadata_service.chord.tests.helpers import ProjectTestCase
from chord_metadata_service.chord.models import ProjectJsonSchema
from chord_metadata_service.patients.models import Individual
from chord_metadata_service.phenopackets.models import Biosample, Phenopacket, Procedure, MetaData
from chord_metadata_service.phenopackets.tests import constants as pheno_consts
from chord_metadata_service.restapi.models import SchemaType


class TestBaseExtraProperties(ProjectTestCase):

    def setUp(self) -> None:
        BASE_PJS = {
            "project": self.project,
            "required": False,
            "json_schema": {"type": "object"},
        }
        self.individual_pjs = ProjectJsonSchema.objects.create(
            **BASE_PJS,
            schema_type=SchemaType.INDIVIDUAL
        )
        self.biosample_pjs = ProjectJsonSchema.objects.create(
            **BASE_PJS,
            schema_type=SchemaType.BIOSAMPLE
        )
        self.phenopacket_pjs = ProjectJsonSchema.objects.create(
            **BASE_PJS,
            schema_type=SchemaType.PHENOPACKET
        )

        self.individual = Individual.objects.create(**pheno_consts.VALID_INDIVIDUAL_1)
        procedure = Procedure.objects.create(**pheno_consts.VALID_PROCEDURE_1)
        self.biosample = Biosample.objects.create(**pheno_consts.valid_biosample_1(self.individual, procedure))
        meta_data = MetaData.objects.create(
            created_by="test",
            submitted_by="test"
        )
        self.phenopacket = Phenopacket.objects.create(
            id="phenopacket_id:1",
            subject=self.individual,
            meta_data=meta_data,
            dataset=self.dataset
        )
        self.phenopacket.biosamples.set([self.biosample])

        # Does not belong to a project
        self.no_proj_phenopacket = Phenopacket.objects.create(
            id="phenopacket_id:2",
            subject=self.individual,
            meta_data=meta_data,
        )

    def test_base_extra_properties(self):
        self.assertIsNotNone(self.individual.get_json_schema())
        self.assertIsNotNone(self.biosample.get_json_schema())
        self.assertIsNotNone(self.phenopacket.get_json_schema())

        self.assertIsNone(self.no_proj_phenopacket.get_json_schema())
        self.assertIsNone(self.no_proj_phenopacket.get_project_id())

    def test_validate_json_schema(self):
        invalid_individual = Individual(**{
            **pheno_consts.VALID_INDIVIDUAL_1,
            "extra_properties": "invalid extra_properties of type 'string', expects 'object'"
        })
        with self.assertRaises(ValidationError):
            invalid_individual.save()
