from rest_framework.test import APITestCase
from rest_framework.test import APIRequestFactory
from chord_metadata_service.chord.models import *
from chord_metadata_service.phenopackets.models import *
from chord_metadata_service.patients.models import Individual
from .constants import INVALID_INGEST_BODY, INVALID_FHIR_BUNDLE_1
from chord_metadata_service.chord.tests.constants import VALID_DATA_USE_1
from chord_metadata_service.chord.data_types import DATA_TYPE_PHENOPACKET
import copy
import uuid


class TestFhirIngest(APITestCase):

    def setUp(self) -> None:
        p = Project.objects.create(title="Project 1", description="Test")
        self.d = Dataset.objects.create(title="Dataset 1", description="Test dataset", data_use=VALID_DATA_USE_1,
                                        project=p)
        to = TableOwnership.objects.create(table_id=uuid.uuid4(), service_id=uuid.uuid4(), service_artifact="metadata",
                                           dataset=self.d)
        self.t = Table.objects.create(ownership_record=to, name="Table 1", data_type=DATA_TYPE_PHENOPACKET)

    # def test_ingest_body(self):
    #     factory = APIRequestFactory()
    #     request = factory.post('/private/ingest-fhir', INVALID_INGEST_BODY, format='json')
    #     with self.assertRaises(ValidationError):
    #         try:
    #             ingest_fhir(request)
    #         except ValidationError as e:
    #             self.assertIn("created_by", e.message)
    #             raise e
    #
    # def test_dataset_id(self):
    #     factory = APIRequestFactory()
    #     invalid_dataset_id_ingest = copy.deepcopy(INVALID_INGEST_BODY)
    #     invalid_dataset_id_ingest["metadata"] = {
    #         "created_by": "Name"
    #     }
    #     request = factory.post('/private/ingest-fhir', invalid_dataset_id_ingest, format='json')
    #     response = ingest_fhir(request)
    #     self.assertEqual(response.status_code, 400)
