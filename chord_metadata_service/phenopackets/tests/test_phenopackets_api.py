import uuid
import responses
import requests
from django.test import TestCase, Client, modify_settings, override_settings
from django.conf import settings
from ..models import Phenopacket, MetaData
from chord_metadata_service.patients.models import Individual
from chord_metadata_service.chord.models import Project, Dataset, TableOwnership, Table


class PhenopacketsAPITest(TestCase):
    """
    Unit tests for the /api/phenopackets endpoint.
    """
    def setUp(self):
        self.client = Client()

        project = Project.objects.create(title="project1")

        self.dataset1 = Dataset.objects.create(title="dataset1", project=project, data_use={})
        self.dataset2 = Dataset.objects.create(title="dataset2", project=project, data_use={})

        table_ownership1 = TableOwnership.objects.create(table_id=uuid.UUID("1f65dce9-c602-4035-b69f-1e9a97b49e3e"),
                                                         service_id="table1", dataset=self.dataset1)
        table_ownership2 = TableOwnership.objects.create(table_id=uuid.UUID("206e1edf-e2a0-4625-848d-e4d1ccd1c203"),
                                                         service_id="table2", dataset=self.dataset2)

        table1 = Table.objects.create(ownership_record=table_ownership1, name="table1", data_type="phenopackets")
        table2 = Table.objects.create(ownership_record=table_ownership2, name="table2", data_type="phenopackets")

        metadata1 = MetaData.objects.create(created_by="test")
        metadata2 = MetaData.objects.create(created_by="test")
        metadata3 = MetaData.objects.create(created_by="test")

        individual1 = Individual.objects.create(id="patient1")
        individual2 = Individual.objects.create(id="patient2")
        individual3 = Individual.objects.create(id="patient3")

        self.phenopacket1 = Phenopacket.objects.create(id=uuid.UUID("8aa21284-857e-46c3-a0b2-4426ca180253"),
                                                       subject=individual1, meta_data=metadata1, table=table1)
        self.phenopacket2 = Phenopacket.objects.create(id=uuid.UUID("7dcf005c-abe8-4631-88c7-edb06e096eee"),
                                                       subject=individual2, meta_data=metadata2, table=table1)
        self.phenopacket3 = Phenopacket.objects.create(id=uuid.UUID("ef7fb959-7fa3-4707-9db6-d6b4cf5f790d"),
                                                       subject=individual3, meta_data=metadata3, table=table2)

    @modify_settings(MIDDLEWARE={
        "remove": "chord_metadata_service.restapi.authz_middleware.AuthzMiddleware",
    })
    def test_without_middleware(self):
        """
        Tests the endpoint when the middleware is not used. Endpoint should return all phenopackets.
        """
        response = self.client.get("/api/phenopackets")
        response_body = response.json()
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response_body["count"], 3)
        correct_phenopackets_response = [self.phenopacket1.id, self.phenopacket2.id, self.phenopacket3.id]
        for phenopacket in response_body["results"]:
            self.assertTrue(uuid.UUID(phenopacket["id"]) in correct_phenopackets_response)
            correct_phenopackets_response.remove(uuid.UUID(phenopacket["id"]))

    @override_settings(CANDIG_OPA_URL="http://127.0.0.1:8180")
    @responses.activate
    def test_with_middleware_filter_one_dataset(self):
        """
        Tests the endpoint when OPA returns one dataset. Endpoint should return all phenopackets in this dataset.
        """
        responses.add(
            responses.POST,
            url=settings.CANDIG_OPA_URL + "/v1/data/permissions",
            json={
                "datasets": [str(self.dataset2.identifier)]
            },
            status=200
        )

        response = self.client.get("/api/phenopackets")
        response_body = response.json()
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response_body["count"], 1)
        phenopacket = response_body["results"][0]
        self.assertTrue(uuid.UUID(phenopacket["id"]) == self.phenopacket3.id)

    @override_settings(CANDIG_OPA_URL="http://127.0.0.1:8180")
    @responses.activate
    def test_with_middleware_filter_no_datasets(self):
        """
        Tests the endpoint when OPA does not return any datasets. Endpoint should not return any phenopackets.
        """
        responses.add(
            responses.POST,
            url=settings.CANDIG_OPA_URL + "/v1/data/permissions",
            json={
                "datasets": []
            },
            status=200
        )

        response = self.client.get("/api/phenopackets")
        response_body = response.json()
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response_body["count"], 0)

    @override_settings(CANDIG_OPA_URL="http://127.0.0.1:8180")
    @responses.activate
    def test_with_middleware_filter_all_datasets(self):
        """
        Tests the endpoint when OPA returns all datasets. Endpoint should return all phenopackets.
        """
        responses.add(
            responses.POST,
            url=settings.CANDIG_OPA_URL + "/v1/data/permissions",
            json={
                "datasets": [str(self.dataset1.identifier), str(self.dataset2.identifier)]
            },
            status=200
        )

        response = self.client.get("/api/phenopackets")
        response_body = response.json()
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response_body["count"], 3)
        correct_phenopackets_response = [self.phenopacket1.id, self.phenopacket2.id, self.phenopacket3.id]
        for phenopacket in response_body["results"]:
            self.assertTrue(uuid.UUID(phenopacket["id"]) in correct_phenopackets_response)
            correct_phenopackets_response.remove(uuid.UUID(phenopacket["id"]))

    @override_settings(CANDIG_OPA_URL="http://127.0.0.1:8180")
    @responses.activate
    def test_with_middleware_opa_is_down(self):
        """
        Tests the endpoint when OPA is down. Endpoint should return status code 500.
        """
        responses.add(
            responses.POST,
            url=settings.CANDIG_OPA_URL + "/v1/data/permissions",
            body=requests.exceptions.RequestException()
        )

        response = self.client.get("/api/phenopackets")
        self.assertEqual(response.status_code, 500)
