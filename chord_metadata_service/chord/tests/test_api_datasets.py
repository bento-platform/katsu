import json
import uuid
import re
from aioresponses import aioresponses
from django.urls import reverse
from rest_framework import status

from chord_metadata_service.authz.tests.helpers import AuthzAPITestCase, mock_authz_eval_one_result
from chord_metadata_service.chord.models import Dataset
from chord_metadata_service.phenopackets.models import Phenopacket
from chord_metadata_service.phenopackets.tests.helpers import PhenoTestCase
from chord_metadata_service.chord.data_types import DATA_TYPES, DATA_TYPE_PHENOPACKET, DATA_TYPE_EXPERIMENT
from chord_metadata_service.experiments.models import Experiment
from chord_metadata_service.chord.tests import constants


class DatasetsTest(AuthzAPITestCase, PhenoTestCase):

    def setUp(self) -> None:
        super().setUp()
        self.entities_by_data_type = {
            DATA_TYPE_PHENOPACKET: {
                'class': Phenopacket,
                'entity': self.phenopacket,
            },
            DATA_TYPE_EXPERIMENT: {
                'class': Experiment,
                'entity': self.experiment
            }
        }

    def test_list_datasets(self):
        r = self.client.get(reverse("chord-dataset-list"))
        self.assertEqual(r.status_code, status.HTTP_200_OK)
        self.assertEqual(1, r.data["count"])
        self.assertEqual(self.dataset.title, r.data["results"][0]["title"])

    def test_get_dataset(self):
        r = self.client.get(reverse("chord-dataset-detail", kwargs={"dataset_id": self.dataset.identifier}))
        self.assertEqual(r.status_code, status.HTTP_200_OK)
        self.assertEqual(str(self.dataset.identifier), r.data["identifier"])
        self.assertEqual(self.dataset.title, r.data["title"])
        self.assertEqual(str(self.project.identifier), str(r.data["project"]))

    def test_del_dataset(self):
        with aioresponses() as m:
            mock_authz_eval_one_result(m, True)
            r = self.client.delete(reverse("chord-dataset-detail", kwargs={"dataset_id": self.dataset.identifier}))
        self.assertEqual(r.status_code, status.HTTP_204_NO_CONTENT)
        with self.assertRaises(Dataset.DoesNotExist):
            self.dataset.refresh_from_db()

    def test_dataset_summary(self):
        r = self.dt_authz_full_get(reverse("chord-dataset-summary", kwargs={"dataset_id": self.dataset.identifier}))
        self.assertEqual(r.status_code, status.HTTP_200_OK)

    def test_dataset_datatype_summary(self):
        r = self.dt_authz_full_get(
            reverse("chord-dataset-data-type-summary", kwargs={"dataset_id": self.dataset.identifier}))
        self.assertEqual(r.status_code, status.HTTP_200_OK)

        bad_dataset_id = str(uuid.uuid4())
        with self.assertRaises(Dataset.DoesNotExist):
            r = self.dt_authz_full_get(
                reverse("chord-dataset-data-type-summary", kwargs={"dataset_id": bad_dataset_id}))
            self.assertEqual(r.status_code, status.HTTP_400_BAD_REQUEST)

    def test_get_dataset_datatype(self):
        for dt in DATA_TYPES:
            if DATA_TYPES[dt]['queryable']:
                url = reverse("chord-dataset-data-type", kwargs={
                    "dataset_id": self.dataset.identifier,
                    "data_type": dt
                })

                r = self.dt_authz_full_get(url)
                self.assertEqual(r.status_code, status.HTTP_200_OK)
                c = r.json()
                self.assertIn("last_ingested", c)
                # Check timestamp format for last_ingested
                timestamp_pattern = re.compile(r"\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}\.\d{6}Z")
                self.assertTrue(timestamp_pattern.match(c["last_ingested"]))
                del c["last_ingested"]

                self.assertDictEqual(c, {
                    "id": dt,
                    "label": "Clinical Data",
                    **DATA_TYPES[dt],
                    "queryable": True,
                    "count": 1
                })

                r = self.dt_authz_none_get(url)
                self.assertEqual(r.status_code, status.HTTP_200_OK)
                c = r.json()
                self.assertIn("last_ingested", c)
                # Check timestamp format for last_ingested
                timestamp_pattern = re.compile(r"\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}\.\d{6}Z")
                self.assertTrue(timestamp_pattern.match(c["last_ingested"]))
                del c["last_ingested"]

                self.assertDictEqual(c, {
                    "id": dt,
                    "label": "Clinical Data",
                    **DATA_TYPES[dt],
                    "queryable": True,
                    # no count - no permissions to see it
                })

    def test_del_dataset_datatype(self):
        for dt in DATA_TYPES:
            if DATA_TYPES[dt]['queryable']:
                with aioresponses() as m:
                    mock_authz_eval_one_result(m, True)
                    r = self.client.delete(
                        reverse("chord-dataset-data-type", kwargs={
                            "dataset_id": self.dataset.identifier,
                            "data_type": dt
                        })
                    )
                self.assertEqual(r.status_code, status.HTTP_204_NO_CONTENT)
                with self.assertRaises(self.entities_by_data_type[dt]['class'].DoesNotExist):
                    self.entities_by_data_type[dt]['entity'].refresh_from_db()

    def test_dataset_update(self):
        # Updates a dataset by changing its dats file
        url = f"/api/datasets/{self.dataset.identifier}"
        payload = {
            "data_use": constants.VALID_DATA_USE_1,
            "dats_file": constants.dats_dataset(str(self.project.identifier), ["Creator A", "Creator B"]),
            "description": "Updated description",
            "project": str(self.project.identifier),
            "title": "Updated title"
        }

        with aioresponses() as m:
            mock_authz_eval_one_result(m, True)
            r = self.client.put(
                url,
                data=json.dumps(payload),
                content_type='application/json'
            )
        self.assertEqual(r.status_code, status.HTTP_200_OK)

        # Check the updated dats file
        r = self.client.get(url + "/dats")
        data = r.json()

        self.assertEqual(data["project"], payload["dats_file"]["project"])
