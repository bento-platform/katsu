import json
import csv
import io
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from ..models import Individual
from . import constants as c


class CreateIndividualTest(APITestCase):
    """ Test module for creating an Individual. """

    def setUp(self):

        self.valid_payload = c.VALID_INDIVIDUAL
        self.invalid_payload = c.INVALID_INDIVIDUAL

    def test_create_individual(self):
        """ POST a new individual. """

        response = self.client.post(
            reverse('individual-list'),
            data=json.dumps(self.valid_payload),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Individual.objects.count(), 1)
        self.assertEqual(Individual.objects.get().id, 'patient:1')

    def test_create_invalid_individual(self):
        """ POST a new individual with invalid data. """

        invalid_response = self.client.post(
            reverse('individual-list'),
            data=json.dumps(self.invalid_payload),
            content_type='application/json'
        )
        self.assertEqual(invalid_response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(Individual.objects.count(), 0)


class UpdateIndividualTest(APITestCase):
    """ Test module for updating an existing Individual record. """

    def setUp(self):
        self.individual_one = Individual.objects.create(**c.VALID_INDIVIDUAL)

        self.put_valid_payload = {
            "id": "patient:1",
            "taxonomy": {
                "id": "NCBITaxon:9606",
                "label": "human"
            },
            "date_of_birth": "2001-01-01",
            "age": {
                "start": {
                    "age": "P45Y"
                },
                "end": {
                    "age": "P49Y"
                }
            },
            "sex": "FEMALE",
            "active": False
        }

        self.invalid_payload = c.INVALID_INDIVIDUAL

    def test_update_individual(self):
        """ PUT new data in an existing Individual record. """

        response = self.client.put(
            reverse(
                'individual-detail',
                kwargs={'pk': self.individual_one.id}
                ),
            data=json.dumps(self.put_valid_payload),
            content_type='application/json'
            )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_update_invalid_individual(self):
        """ PUT new invalid data in an existing Individual record. """

        response = self.client.put(
            reverse(
                'individual-detail',
                kwargs={'pk': self.individual_one.id}
                ),
            data=json.dumps(self.invalid_payload),
            content_type='application/json'
            )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


class DeleteIndividualTest(APITestCase):
    """ Test module for deleting an existing Individual record. """

    def setUp(self):
        self.individual_one = Individual.objects.create(**c.VALID_INDIVIDUAL)

    def test_delete_individual(self):
        """ DELETE an existing Individual record. """

        response = self.client.delete(
            reverse(
                'individual-detail',
                kwargs={'pk': self.individual_one.id}
                )
            )
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    def test_delete_non_existing_individual(self):
        """ DELETE a non-existing Individual record. """

        response = self.client.delete(
            reverse(
                'individual-detail',
                kwargs={'pk': 'patient:what'}
                )
            )
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)


class IndividualCSVRendererTest(APITestCase):
    """ Test csv export for Individuals. """

    def setUp(self):
        self.individual_one = Individual.objects.create(**c.VALID_INDIVIDUAL)

    def test_csv_export(self):
        get_resp = self.client.get('/api/individuals?format=csv')
        self.assertEqual(get_resp.status_code, status.HTTP_200_OK)
        content = get_resp.content.decode('utf-8')
        cvs_reader = csv.reader(io.StringIO(content))
        body = list(cvs_reader)
        self.assertEqual(body[1][1], c.VALID_INDIVIDUAL['sex'])
        headers = body.pop(0)
        for column in ['id', 'sex', 'date of birth', 'taxonomy', 'karyotypic sex',
                       'race', 'ethnicity', 'age', 'diseases', 'created', 'updated']:
            self.assertIn(column, [column_name.lower() for column_name in headers])


class IndividualFullTextSearchTest(APITestCase):
    """ Test for api/individuals?search= """

    def setUp(self):
        self.individual_one = Individual.objects.create(**c.VALID_INDIVIDUAL)
        self.individual_two = Individual.objects.create(**c.VALID_INDIVIDUAL_2)

    def test_search(self):
        get_resp_1 = self.client.get('/api/individuals?search=P49Y')
        self.assertEqual(get_resp_1.status_code, status.HTTP_200_OK)
        response_obj_1 = get_resp_1.json()
        self.assertEqual(len(response_obj_1['results']), 1)

        get_resp_2 = self.client.get('/api/individuals?search=NCBITaxon:9606')
        self.assertEqual(get_resp_2.status_code, status.HTTP_200_OK)
        response_obj_2 = get_resp_2.json()
        self.assertEqual(len(response_obj_2['results']), 2)


class PublicListIndividualsTest(APITestCase):
    """ Test for api/public """

    response_threshold = 5

    @staticmethod
    def response_threshold_check(response):
        return response['count'] if "count" in response else "Not enough data."

    def setUp(self):
        individuals = [c.generate_valid_individual() for _ in range(27)]  # random range
        for individual in individuals:
            Individual.objects.create(**individual)

    def test_public_get(self):
        response = self.client.get('/api/public')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        response_obj = response.json()
        self.assertIn(
            self.response_threshold_check(response_obj),
            [Individual.objects.all().count(), "Not enough data."]
        )
        if Individual.objects.all().count() < self.response_threshold:
            self.assertEqual(response_obj, "Not enough data.")

    def test_public_filtering_sex(self):
        response = self.client.get('/api/public?sex=female')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        response_obj = response.json()
        self.assertIn(
            self.response_threshold_check(response_obj),
            [Individual.objects.filter(sex__iexact='female').count(), "Not enough data."]
        )
        if Individual.objects.filter(sex__iexact='female').count() < self.response_threshold:
            self.assertEqual(response_obj, "Not enough data.")

    def test_public_filtering_2_fields(self):

        # test GET query string search for extra_properties field
        response = self.client.get('/api/public?sex=female&extra_properties="smoking": "Non-smoker"')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        response_obj = response.json()
        db_count = Individual.objects.filter(sex__iexact='female')\
            .filter(extra_properties__contains={"smoking": "Non-smoker"}).count()
        self.assertIn(self.response_threshold_check(response_obj), [db_count, "Not enough data."])
        if db_count < self.response_threshold:
            self.assertEqual(response_obj, "Not enough data.")

    def test_public_filtering_extra_properties_1(self):
        # whitespaces
        response_1 = self.client.get('/api/public?extra_properties="smoking": "Non-smoker", "death": "deceased"')
        self.assertEqual(response_1.status_code, status.HTTP_200_OK)
        response_obj_1 = response_1.json()
        db_count_1 = Individual.objects\
            .filter(extra_properties__contains={"smoking": "Non-smoker"})\
            .filter(extra_properties__contains={"death": "Deceased"})\
            .count()
        self.assertIn(self.response_threshold_check(response_obj_1), [db_count_1, "Not enough data."])
        if db_count_1 < self.response_threshold:
            self.assertEqual(response_obj_1, "Not enough data.")

        # no whitespaces
        response_2 = self.client.get('/api/public?extra_properties="smoking":"Non-smoker","death":"deceased"')
        response_obj_2 = response_2.json()
        self.assertIn(self.response_threshold_check(response_obj_2), [db_count_1, "Not enough data."])
        if db_count_1 < self.response_threshold:
            self.assertEqual(response_obj_2, "Not enough data.")

        # random whitespaces
        response_3 = self.client.get('/api/public?extra_properties="smoking": "Non-smoker", "death":"deceased"')
        response_obj_3 = response_3.json()
        self.assertIn(self.response_threshold_check(response_obj_3), [db_count_1, "Not enough data."])
        if db_count_1 < self.response_threshold:
            self.assertEqual(response_obj_3, "Not enough data.")

    def test_public_filtering_extra_properties_2(self):

        # add more values
        response = self.client.get(
            '/api/public?extra_properties="smoking": "Non-smoker", "death": "deceased","test_result": "positive"'
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        response_obj = response.json()
        db_count = Individual.objects.filter(
            extra_properties__contains={"smoking": "Non-smoker", "death": "Deceased", "test_result": "Positive"}
        ).count()
        self.assertIn(self.response_threshold_check(response_obj), [db_count, "Not enough data."])
        if db_count < self.response_threshold:
            self.assertEqual(response_obj, "Not enough data.")
