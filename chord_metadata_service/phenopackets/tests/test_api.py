import csv
import io
import uuid

from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from chord_metadata_service.authz.tests.helpers import AuthzAPITestCase
from chord_metadata_service.chord.dataset_schema import KatsuDatasetModel
from chord_metadata_service.chord.models import Project, Dataset
from chord_metadata_service.chord.ingest import WORKFLOW_INGEST_FUNCTION_MAP
from chord_metadata_service.chord.workflows.metadata import WORKFLOW_PHENOPACKETS_JSON
from chord_metadata_service.chord.tests.constants import VALID_DATASET_PRIMARY_CONTACT
from chord_metadata_service.geo.tests.constants import KINGSTON_GEOM_JSON
from chord_metadata_service.logger import logger
from chord_metadata_service.restapi.tests import constants as restapi_c

from . import constants as c
from ..schemas import PHENOPACKET_SCHEMA
from .. import models as m, serializers as s


class CreateBiosampleTest(AuthzAPITestCase):
    """ Test module for creating an Biosample. """

    def setUp(self):
        self.individual = m.Individual.objects.create(**c.VALID_INDIVIDUAL_1)
        self.procedure = c.VALID_PROCEDURE_1
        self.valid_payload = c.valid_biosample_1(self.individual.id, self.procedure)
        self.invalid_payload = {
            "id": "biosample:1",
            "individual": self.individual.id,
            "procedure": self.procedure,
            "description": "This is a test description.",
            "sampled_tissue": {
                "id": "UBERON_0001256"
            },
            "histological_diagnosis": {
                "id": "NCIT:C39853",
                "label": "Infiltrating Urothelial Carcinoma"
            },
            "tumor_progression": {
                "id": "NCIT:C84509",
                "label": "Primary Malignant Neoplasm"
            },
            "tumor_grade": {
                "id": "NCIT:C48766",
                "label": "pT2b Stage Finding"
            },
            "diagnostic_markers": [
                {
                    "id": "NCIT:C49286",
                    "label": "Hematology Test"
                },
                {
                    "id": "NCIT:C15709",
                    "label": "Genetic Testing"
                }
            ]
        }
        self.procedure_age_performed = {
            "age": {
                "iso_8601_duration": "P25Y"
            }
        }

    def test_create_biosample(self):
        """ POST a new biosample. """

        response = self.one_authz_post(reverse("biosamples-list"), json=self.valid_payload)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(m.Biosample.objects.count(), 1)
        self.assertEqual(m.Biosample.objects.get().id, 'katsu.biosample_id:1')

    def test_create_biosample_forbidden(self):
        """ POST a new biosample. """

        response = self.one_no_authz_post(reverse("biosamples-list"), json=self.valid_payload)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_create_invalid_biosample(self):
        """ POST a new biosample with invalid data. """

        invalid_response = self.one_authz_post(reverse('biosamples-list'), self.invalid_payload)
        self.assertEqual(
            invalid_response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(m.Biosample.objects.count(), 0)

    def test_serializer_validate_invalid(self):
        serializer = s.BiosampleSerializer(data=self.invalid_payload)
        self.assertEqual(serializer.is_valid(), False)

    def test_serializer_validate_valid(self):
        serializer = s.BiosampleSerializer(data=self.valid_payload)
        self.assertEqual(serializer.is_valid(), True)

    def test_create_biosample_with_location(self):
        response = self.one_authz_post(reverse("biosamples-list"), json={
            **self.valid_payload,
            "location_collected": {
                "type": "Feature",
                "geometry": KINGSTON_GEOM_JSON,
                "properties": {
                    "label": "Kingston",
                    "abc": "def",
                },
            },
        })
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(m.Biosample.objects.count(), 1)
        self.assertEqual(m.Biosample.objects.get().location_collected.label, "Kingston")
        self.assertDictEqual(m.Biosample.objects.get().location_collected.extra_properties, {"abc": "def"})

    def test_create_biosample_with_invalid_location(self):
        response = self.one_authz_post(reverse("biosamples-list"), json={
            **self.valid_payload,
            "location_collected": {
                "type": "Feature",
                "geometry": KINGSTON_GEOM_JSON,
                "properties": ["a", "b", "c"],  # not a dict
            },
        })
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        with self.assertRaises(m.Biosample.DoesNotExist):
            m.Biosample.objects.get()


class UpdateBiosampleTest(AuthzAPITestCase):
    def setUp(self):
        self.individual = m.Individual.objects.create(**c.VALID_INDIVIDUAL_1)
        self.procedure = c.VALID_PROCEDURE_1
        self.valid_payload = c.valid_biosample_1(self.individual.id, self.procedure)

        self.procedure_age_performed = {
            "age": {
                "iso_8601_duration": "P25Y"
            }
        }

        self.location_collected_patch = {
            "location_collected": {
                "type": "Feature",
                "geometry": KINGSTON_GEOM_JSON,
                "properties": {},
            },
        }

        # Create initial biosample
        response = self.one_authz_post(reverse("biosamples-list"), json=self.valid_payload)
        self.biosample_id = response.data['id']

    def test_update(self):
        # Should be 1
        initial_count = m.Biosample.objects.all().count()

        # Update the biosample.procedure.performed field
        response = self.one_authz_put(
            f"/api/biosamples/{self.biosample_id}",
            json={
                **self.valid_payload,
                "procedure": {
                    **self.valid_payload["procedure"],
                    "performed": self.procedure_age_performed,
                },
            }
        )

        # Should be 1 as well
        post_update_count = m.Biosample.objects.all().count()
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(initial_count, post_update_count)
        self.assertEqual(response.data['procedure']['performed'], self.procedure_age_performed)

    def test_update_biosample_location(self):
        r = self.one_authz_patch(f"/api/biosamples/{self.biosample_id}", json=self.location_collected_patch)
        self.assertEqual(r.status_code, status.HTTP_200_OK)

        r = self.one_authz_get(f"/api/biosamples/{self.biosample_id}")
        self.assertDictEqual(r.json()["location_collected"], self.location_collected_patch["location_collected"])

    def test_update_biosample_forbidden(self):
        r = self.one_no_authz_patch(f"/api/biosamples/{self.biosample_id}")
        self.assertEqual(r.status_code, status.HTTP_403_FORBIDDEN)


class BatchBiosamplesCSVTest(AuthzAPITestCase):
    def setUp(self):
        self.individual = m.Individual.objects.create(**c.VALID_INDIVIDUAL_1)
        self.valid_payload = c.valid_biosample_1(self.individual)
        self.biosample = m.Biosample.objects.create(**self.valid_payload)
        self.view = 'batch/biosamples-list'
        self.post_biosamples_body = {
            'id': [str(self.biosample.id)],
            'format': 'csv'
        }

    def test_get_all_biosamples_batch(self):
        response = self.one_authz_get(reverse(self.view))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)

    def test_get_all_biosamples_batch_forbidden(self):
        response = self.one_no_authz_get(reverse(self.view))
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_post_biosamples_with_ids(self):
        response = self.one_authz_post(reverse(self.view), json=self.post_biosamples_body)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        content = response.content.decode('utf-8')
        csv_reader = csv.reader(io.StringIO(content))
        body = list(csv_reader)
        headers = body.pop(0)
        for column in ['id', 'description', 'sampled tissue',
                       'time of collection',
                       'histological diagnosis', 'extra properties',
                       'created', 'updated', 'individual']:
            self.assertIn(column, [column_name.lower() for column_name in headers])

    def test_post_biosamples_with_ids_forbidden(self):
        response = self.one_no_authz_post(reverse(self.view), json=self.post_biosamples_body)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        # TODO: test content

    def test_post_biosamples_with_selected_fields(self):
        response = self.one_authz_post(
            reverse(self.view), json={**self.post_biosamples_body, 'fields': ['id', 'description']}
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        headers = next(csv.reader(io.StringIO(response.content.decode('utf-8'))))
        self.assertEqual(headers, ['Id', 'Description'])

    def test_post_biosamples_unknown_field_error(self):
        response = self.one_authz_post(
            reverse(self.view), json={**self.post_biosamples_body, 'fields': ['id', 'not_a_real_field']}
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('not_a_real_field', response.json()['errors'][0]['message'])

    def test_get_biosamples_batch_unknown_field_error(self):
        response = self.one_authz_get(reverse(self.view) + '?format=csv&fields=not_a_real_field')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('not_a_real_field', response.json()['errors'][0]['message'])

    def test_export_fields_action(self):
        response = self.one_authz_get(reverse('batch/biosamples-export-fields'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        keys = [f['key'] for f in response.json()]
        self.assertEqual(
            keys,
            ['id', 'description', 'sampled_tissue', 'time_of_collection', 'histological_diagnosis',
             'extra_properties', 'created', 'updated', 'individual'],
        )

    def test_export_fields_action_forbidden(self):
        response = self.one_no_authz_get(reverse('batch/biosamples-export-fields'))
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)


class CreatePhenopacketTest(AuthzAPITestCase):

    def setUp(self):
        individual = m.Individual.objects.create(**c.VALID_INDIVIDUAL_1)
        self.subject = individual.id
        meta = m.MetaData.objects.create(**c.VALID_META_DATA_2)
        self.metadata = meta.id
        self.phenopacket = c.valid_phenopacket(
            subject=self.subject,
            meta_data=self.metadata)

    def test_phenopacket_create(self):
        response = self.one_authz_post(reverse("phenopackets-list"), json=self.phenopacket)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(m.Phenopacket.objects.count(), 1)

    def test_phenopacket_create_forbidden(self):
        response = self.one_no_authz_post(reverse("phenopackets-list"), json=self.phenopacket)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(m.Phenopacket.objects.count(), 0)

    def test_serializer(self):
        serializer = s.PhenopacketSerializer(data=self.phenopacket)
        self.assertEqual(serializer.is_valid(), True)


class GetPhenopacketsApiTest(AuthzAPITestCase):
    """
    Test that we can retrieve phenopackets with valid dataset titles or without dataset title.
    """

    def setUp(self) -> None:
        """
        Create two datasets and ingest 1 phenopacket into each.
        """
        self.p = Project.objects.create(title="Project 1", description="")
        schema1 = KatsuDatasetModel(
            schema_version="1.0", title="dataset_1", description="Some dataset",
            primary_contact=VALID_DATASET_PRIMARY_CONTACT, project=str(self.p.identifier),
            identifier=str(uuid.uuid4()),
        )
        self.d = Dataset.from_schema(schema1)
        self.d.save()
        self.d.refresh_from_db()
        schema2 = KatsuDatasetModel(
            schema_version="1.0", title="dataset_2", description="Some dataset",
            primary_contact=VALID_DATASET_PRIMARY_CONTACT, project=str(self.p.identifier),
            identifier=str(uuid.uuid4()),
        )
        self.d2 = Dataset.from_schema(schema2)
        self.d2.save()
        self.d2.refresh_from_db()

        WORKFLOW_INGEST_FUNCTION_MAP[WORKFLOW_PHENOPACKETS_JSON](
            restapi_c.VALID_PHENOPACKET_1, self.d.identifier, logger)
        WORKFLOW_INGEST_FUNCTION_MAP[WORKFLOW_PHENOPACKETS_JSON](
            restapi_c.VALID_PHENOPACKET_2, self.d2.identifier, logger)

    def test_get_phenopackets_no_access(self):
        """
        Test that we cannot get the complete set of phenopackets without authorization.
        """
        response = self.one_no_authz_get("/api/phenopackets")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_get_phenopackets(self):
        """
        Test that we can get 2 phenopackets without a dataset title.
        """
        response = self.one_authz_get("/api/phenopackets")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.json()["results"]), 2)

    def test_get_phenopackets_with_valid_dataset_via_scope(self):
        """
        Test that we can get 1 phenopacket under dataset_1 via discovery scoping.
        """
        response = self.one_authz_get(f"/api/phenopackets?dataset={self.d.identifier}")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        response_data = response.json()
        self.assertEqual(len(response_data["results"]), 1)
        self.assertEqual(response_data["results"][0]["project"], str(self.p.identifier))
        self.assertEqual(response_data["results"][0]["dataset"], str(self.d.identifier))

    def test_get_phenopackets_with_valid_dataset_via_scope_no_access(self):
        """
        Test that we can get 1 phenopacket under dataset_1 via discovery scoping.
        """
        response = self.one_no_authz_get(f"/api/phenopackets?dataset={self.d.identifier}")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_get_phenopackets_with_valid_dataset_via_filter(self):
        """
        Test that we can get phenopackets under specific datasets via title using Django filter.
        """

        subtest_params = [
            ("dataset_1", 1),
            ("dataset_2", 1),
            ("dataset_1,dataset_2", 2),
            ("dataset_1,noSuchDataset", 1),
            ("notADataset", 0),
        ]

        for params in subtest_params:
            with self.subTest(params=params):
                ds_title, exp_count = params
                response = self.one_authz_get(f"/api/phenopackets?datasets={ds_title}")
                self.assertEqual(response.status_code, status.HTTP_200_OK)
                response_data = response.json()
                self.assertEqual(len(response_data["results"]), exp_count)


class PhenopacketSchema(APITestCase):
    # No authz needed for these endpoints

    def test_get_phenopacket_schema(self):
        response = self.client.get("/api/schemas/phenopacket")
        schema = response.json()
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(schema, PHENOPACKET_SCHEMA)

    def test_get_pheno_subschemas(self):
        for subschema in PHENOPACKET_SCHEMA["properties"].values():
            prop_key = subschema["$id"].split('/')[-1]
            response = self.client.get(reverse("chord-phenopacket-subschema", kwargs={"subschema": prop_key}))
            self.assertEqual(response.status_code, status.HTTP_200_OK)
            self.assertEqual(response.json(), subschema)
