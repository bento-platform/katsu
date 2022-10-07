from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from chord_metadata_service.chord.tests.constants import (
    VALID_PROJECT_1,
    VALID_DATS_CREATORS,
    dats_dataset,
)
from chord_metadata_service.restapi.tests.utils import get_response
import json


class JSONLDDatasetTest(APITestCase):
    def setUp(self) -> None:
        project = get_response('project-list', VALID_PROJECT_1)
        self.project = project.json()
        self.creators = VALID_DATS_CREATORS
        self.dataset = dats_dataset(self.project['identifier'], self.creators)
        client = APIClient()
        client.post(
            '/api/datasets',
            data=json.dumps(self.dataset),
            content_type='application/json'
        )

    def test_jsonld(self):
        get_resp = self.client.get('/api/datasets?format=json-ld')
        get_resp_obj = get_resp.json()
        self.assertEqual(get_resp.status_code, status.HTTP_200_OK)
        self.assertIsInstance(get_resp_obj['results'][0]['@context'], list)
        self.assertIsNotNone(get_resp_obj['results'][0]['@context'], True)
        self.assertEqual(get_resp_obj['results'][0]['@type'], 'Dataset')

    def test_rdf(self):
        get_resp = self.client.get('/api/datasets?format=rdf')
        self.assertEqual(get_resp.status_code, status.HTTP_200_OK)
        self.assertEqual(get_resp.accepted_media_type, 'application/rdf+xml')
        self.assertIsInstance(get_resp.content, bytes)
