import os

from django.core.exceptions import ValidationError
from rest_framework.test import APITestCase

from chord_metadata_service.chord.models import Project, Dataset
from chord_metadata_service.chord.ingest import WORKFLOW_INGEST_FUNCTION_MAP
from chord_metadata_service.chord.tests.constants import VALID_DATA_USE_1
from chord_metadata_service.chord.workflows.metadata import WORKFLOW_FHIR_JSON
from chord_metadata_service.patients.models import Individual
from chord_metadata_service.phenopackets.models import PhenotypicFeature, Biosample, Disease, Procedure, Phenopacket
from chord_metadata_service.restapi.fhir_ingest import ingest_patients, ingest_observations
from .constants import INVALID_FHIR_BUNDLE_1, INVALID_SUBJECT_NOT_PRESENT


EXAMPLE_INGEST_OUTPUTS = {
    "patients": os.path.join(os.path.dirname(__file__), "example_fhir_patients.json"),
    "observations": os.path.join(os.path.dirname(__file__), "example_fhir_observations.json"),
    "conditions": os.path.join(os.path.dirname(__file__), "example_fhir_conditions.json"),
    "specimens": os.path.join(os.path.dirname(__file__), "example_fhir_specimens.json"),
}


class TestFhirIngest(APITestCase):

    def setUp(self) -> None:
        p = Project.objects.create(title="Project 1", description="Test")
        self.d = Dataset.objects.create(title="Dataset 1", description="Test dataset", data_use=VALID_DATA_USE_1,
                                        project=p)

    def test_fhir_bundle_schema(self):

        with self.assertRaises(ValidationError):
            try:
                ingest_patients(INVALID_FHIR_BUNDLE_1, self.d, "Test")
            except ValidationError as e:
                self.assertIn("resourceType", e.message)
                raise e

    def test_required_subject(self):

        with self.assertRaises(KeyError):
            try:
                ingest_observations({}, INVALID_SUBJECT_NOT_PRESENT)
            except KeyError as e:
                raise e

    def test_ingest_fhir(self):
        WORKFLOW_INGEST_FUNCTION_MAP[WORKFLOW_FHIR_JSON](EXAMPLE_INGEST_OUTPUTS, self.d.identifier)
        self.assertTrue(len(Individual.objects.all()) >= 1)
        self.assertTrue(len(PhenotypicFeature.objects.all()) >= 1)
        self.assertTrue(len(Biosample.objects.all()) >= 1)
        self.assertTrue(len(Procedure.objects.all()) >= 1)
        self.assertTrue(len(Disease.objects.all()) >= 1)
        self.assertTrue(len(Phenopacket.objects.all()) >= 1)
