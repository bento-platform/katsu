from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from chord_metadata_service.chord.models import Dataset
from chord_metadata_service.phenopackets.models import Phenopacket

from chord_metadata_service.phenopackets.tests.helpers import PhenoTestCase
from chord_metadata_service.chord.data_types import DATA_TYPES, DATA_TYPE_PHENOPACKET, DATA_TYPE_EXPERIMENT
from chord_metadata_service.experiments.models import Experiment
from chord_metadata_service.experiments.tests import constants as exp_consts

class DatasetsTest(APITestCase, PhenoTestCase):

    def setUp(self) -> None:
        super().setUp()
        self.experiment = Experiment.objects.create(
            **exp_consts.valid_experiment(self.biosample_1, dataset=self.dataset),
        )

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
        r = self.client.delete(reverse("chord-dataset-detail", kwargs={"dataset_id": self.dataset.identifier}))
        self.assertEqual(r.status_code, status.HTTP_204_NO_CONTENT)
        with self.assertRaises(Dataset.DoesNotExist):
            self.dataset.refresh_from_db()

    def test_dataset_summary(self):
        r = self.client.get(reverse("chord-dataset-summary", kwargs={"dataset_id": self.dataset.identifier}))
        self.assertEqual(r.status_code, status.HTTP_200_OK)

    def test_get_dataset_datatype(self):
        for dt in DATA_TYPES:
            if DATA_TYPES[dt]['queryable']:
                r = self.client.get(
                    reverse("chord-dataset-data-type", kwargs={
                        "dataset_id": self.dataset.identifier,
                        "data_type": dt
                    })
                )
                self.assertEqual(r.status_code, status.HTTP_200_OK)
                self.assertEqual(self.entities_by_data_type[dt]['entity'].id, r.data[0]['id'])

    def test_del_dataset_datatype(self):
        for dt in DATA_TYPES:
            if DATA_TYPES[dt]['queryable']:
                r = self.client.delete(
                    reverse("chord-dataset-data-type", kwargs={
                        "dataset_id": self.dataset.identifier,
                        "data_type": dt
                    })
                )
                self.assertEqual(r.status_code, status.HTTP_204_NO_CONTENT)
                with self.assertRaises(self.entities_by_data_type[dt]['class'].DoesNotExist):
                    self.entities_by_data_type[dt]['entity'].refresh_from_db()
