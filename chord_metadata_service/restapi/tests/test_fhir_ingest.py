import uuid

from django.core.exceptions import ValidationError
from rest_framework.test import APITestCase

from chord_metadata_service.chord.data_types import DATA_TYPE_PHENOPACKET
from chord_metadata_service.chord.models import Project, Dataset, TableOwnership, Table
from chord_metadata_service.chord.tests.constants import VALID_DATA_USE_1
from chord_metadata_service.restapi.fhir_ingest import ingest_patients, ingest_observations
from .constants import INVALID_FHIR_BUNDLE_1, INVALID_SUBJECT_NOT_PRESENT


class TestFhirIngest(APITestCase):

    def setUp(self) -> None:
        p = Project.objects.create(title="Project 1", description="Test")
        self.d = Dataset.objects.create(title="Dataset 1", description="Test dataset", data_use=VALID_DATA_USE_1,
                                        project=p)
        to = TableOwnership.objects.create(table_id=uuid.uuid4(), service_id=uuid.uuid4(), service_artifact="metadata",
                                           dataset=self.d)
        self.t = Table.objects.create(ownership_record=to, name="Table 1", data_type=DATA_TYPE_PHENOPACKET)

    def test_fhir_bundle_schema(self):

        with self.assertRaises(ValidationError):
            try:
                ingest_patients(INVALID_FHIR_BUNDLE_1, self.t, "Test")
            except ValidationError as e:
                self.assertIn("resourceType", e.message)
                raise e

    def test_required_subject(self):

        with self.assertRaises(KeyError):
            try:
                ingest_observations({}, INVALID_SUBJECT_NOT_PRESENT)
            except KeyError as e:
                raise e
