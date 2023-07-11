import json
from django.db.utils import IntegrityError

from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from chord_metadata_service.chord.models import Dataset

from chord_metadata_service.chord.tests.helpers import ProjectTestCase
from chord_metadata_service.chord.data_types import DATA_TYPES

class DatasetsTest(APITestCase, ProjectTestCase):

    def setUp(self) -> None:
        return super().setUp()
    
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
        r = self.client.delete(reverse("chord-dataset-detail", kwargs={"dataset_id": self.dataset.identifier}))
        self.assertEqual(r.status_code, status.HTTP_204_NO_CONTENT)
        self.assertRaises(Dataset.DoesNotExist)

    def test_dataset_summary(self):
        r = self.client.get(reverse("chord-dataset-summary", kwargs={"dataset_id": self.dataset.identifier}))
        self.assertEqual(r.status_code, status.HTTP_200_OK)

    def test_get_dataset_datatype(self):
        for dt in DATA_TYPES:
            r = self.client.get(
                reverse("chord-dataset-data-type", kwargs={
                    "dataset_id": self.dataset.identifier,
                    "data_type": dt
                })
            )
        pass

    def test_del_dataset_datatype(self):
        for dt in DATA_TYPES:
            r = self.client.delete(
                reverse("chord-dataset-data-type", kwargs={
                    "dataset_id": self.dataset.identifier,
                    "data_type": dt
                })
            )
            print(r.status_code)
        pass
