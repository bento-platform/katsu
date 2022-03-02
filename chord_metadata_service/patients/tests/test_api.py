import json
import csv
import io
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from chord_metadata_service.patients.models import Individual
from chord_metadata_service.metadata.settings import CONFIG_FIELDS

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
    not_enough_data_response = {'message': 'Insufficient information available.'}

    def response_threshold_check(self, response):
        return response['count'] if 'count' in response else self.not_enough_data_response

    def setUp(self):
        individuals = [c.generate_valid_individual() for _ in range(137)]  # random range
        for individual in individuals:
            Individual.objects.create(**individual)

    def test_public_get(self):
        # no filters GET request to /api/public, returns count or not enough data
        response = self.client.get('/api/public')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        response_obj = response.json()
        self.assertIn(
            self.response_threshold_check(response_obj),
            [Individual.objects.all().count(), self.not_enough_data_response]
        )
        if Individual.objects.all().count() <= self.response_threshold:
            self.assertEqual(response_obj, self.not_enough_data_response)
        else:
            self.assertEqual(Individual.objects.all().count(), response_obj['count'])

    def test_public_filtering_sex(self):
        # sex field search
        response = self.client.get('/api/public?sex=female')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        response_obj = response.json()
        self.assertIn(
            self.response_threshold_check(response_obj),
            [Individual.objects.filter(sex__iexact='female').count(), self.not_enough_data_response]
        )
        if Individual.objects.filter(sex__iexact='female').count() <= self.response_threshold:
            self.assertEqual(response_obj, self.not_enough_data_response)
        else:
            self.assertEqual(Individual.objects.filter(sex__iexact='female').count(), response_obj['count'])

    def test_public_filtering_2_fields(self):
        # sex and extra_properties string search
        # test GET query string search for extra_properties field
        response = self.client.get('/api/public?sex=female&extra_properties=[{"smoking": "Non-smoker"}]')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        response_obj = response.json()
        db_count = Individual.objects.filter(sex__iexact='female')\
            .filter(extra_properties__contains={"smoking": "Non-smoker"}).count()
        if CONFIG_FIELDS:
            self.assertIn(self.response_threshold_check(response_obj), [db_count, self.not_enough_data_response])
            if db_count <= self.response_threshold:
                self.assertEqual(response_obj, self.not_enough_data_response)
            else:
                self.assertEqual(db_count, response_obj['count'])

    def test_public_filtering_extra_properties_1(self):
        # extra_properties string search (multiple values)
        response = self.client.get('/api/public?extra_properties=[{"smoking": "Non-smoker"}, {"death_dc": "Deceased"}]')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        response_obj = response.json()
        db_count = Individual.objects.filter(
            extra_properties__contains={"smoking": "Non-smoker", "death_dc": "Deceased"}
        ).count()
        if CONFIG_FIELDS:
            self.assertIn(self.response_threshold_check(response_obj), [db_count, self.not_enough_data_response])
            if db_count <= self.response_threshold:
                self.assertEqual(response_obj, self.not_enough_data_response)
            else:
                self.assertEqual(db_count, response_obj['count'])

    def test_public_filtering_extra_properties_2(self):
        # extra_properties string search (multiple values)
        response = self.client.get(
            '/api/public?extra_properties=[{"smoking": "Non-smoker"},'
            '{"death_dc": "deceased"},{"covidstatus": "positive"}]'
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        response_obj = response.json()
        db_count = Individual.objects.filter(
            extra_properties__contains={"smoking": "Non-smoker", "death_dc": "Deceased", "covidstatus": "Positive"}
        ).count()
        if CONFIG_FIELDS:
            self.assertIn(self.response_threshold_check(response_obj), [db_count, self.not_enough_data_response])
            if db_count <= self.response_threshold:
                self.assertEqual(response_obj, self.not_enough_data_response)
            else:
                self.assertEqual(db_count, response_obj['count'])

    def test_public_filtering_extra_properties_invalid_1(self):
        # if GET query string doesn't have a list return Not enough data
        response = self.client.get('/api/public?extra_properties="smoking": "Non-smoker","death_dc": "deceased"')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.json(), self.not_enough_data_response)

    def test_public_filtering_extra_properties_invalid_2(self):
        # if GET query string has a random stuff return Not enough data
        response = self.client.get('/api/public?extra_properties=["smoking": "Non-smoker", "5", "Test"]')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.json(), self.not_enough_data_response)

    def test_public_filtering_extra_properties_invalid_3(self):
        # if GET query string list has various data types Not enough data
        response = self.client.get('/api/public?extra_properties=[{"smoking": "Non-smoker"}, 5, "Test"]')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.json(), self.not_enough_data_response)

    def test_public_filtering_extra_properties_range_1(self):
        # extra_properties range search (both min and max ranges, single value)
        response = self.client.get(
            '/api/public?extra_properties=[{"lab_test_result_value": {"rangeMin": 50, "rangeMax": 999}}]'
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        response_obj = response.json()
        # if there is no CONFIG file then the response_obj count is count of all because the filter is ignored
        range_parameters = {
            "extra_properties__lab_test_result_value__gte": 50,
            "extra_properties__lab_test_result_value__lte": 999
        }
        db_count = Individual.objects.filter(**range_parameters).count()
        if CONFIG_FIELDS:
            self.assertIn(self.response_threshold_check(response_obj), [db_count, self.not_enough_data_response])
            if db_count <= self.response_threshold:
                self.assertEqual(response_obj, self.not_enough_data_response)
            else:
                self.assertEqual(db_count, response_obj['count'])

    def test_public_filtering_extra_properties_range_2(self):
        # extra_properties range search (only min range, single value)
        response = self.client.get(
            '/api/public?extra_properties=[{"lab_test_result_value": {"rangeMin": 50}}]'
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        response_obj = response.json()
        # if there is no CONFIG file then the response_obj count is count of all because the filter is ignored
        range_parameters = {
            "extra_properties__lab_test_result_value__gte": 50
        }
        db_count = Individual.objects.filter(**range_parameters).count()
        if CONFIG_FIELDS:
            self.assertIn(self.response_threshold_check(response_obj), [db_count, self.not_enough_data_response])
            if db_count <= self.response_threshold:
                self.assertEqual(response_obj, self.not_enough_data_response)
            else:
                self.assertEqual(db_count, response_obj['count'])

    def test_public_filtering_extra_properties_range_3(self):
        # extra_properties range search (only min range, single value)
        response = self.client.get(
            '/api/public?extra_properties=[{"lab_test_result_value": {"rangeMax": 100}}]'
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        response_obj = response.json()
        # if there is no CONFIG file then the response_obj count is count of all because the filter is ignored
        range_parameters = {
            "extra_properties__lab_test_result_value__lte": 100
        }
        db_count = Individual.objects.filter(**range_parameters).count()
        if CONFIG_FIELDS:
            self.assertIn(self.response_threshold_check(response_obj), [db_count, self.not_enough_data_response])
            if db_count <= self.response_threshold:
                self.assertEqual(response_obj, self.not_enough_data_response)
            else:
                self.assertEqual(db_count, response_obj['count'])

    def test_public_filtering_extra_properties_range_string_1(self):
        # sex string search and extra_properties range search (both min and max ranges, single value)
        response = self.client.get(
            '/api/public?sex=female&extra_properties=[{"lab_test_result_value": {"rangeMin": 5, "rangeMax": 900}}]'
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        response_obj = response.json()
        # if there is no CONFIG file then the response_obj count is count of all because the filter is ignored
        range_parameters = {
            "sex__iexact": "female",
            "extra_properties__lab_test_result_value__gte": 5,
            "extra_properties__lab_test_result_value__lte": 900
        }
        db_count = Individual.objects.filter(**range_parameters).count()
        if CONFIG_FIELDS:
            self.assertIn(self.response_threshold_check(response_obj), [db_count, self.not_enough_data_response])
            if db_count <= self.response_threshold:
                self.assertEqual(response_obj, self.not_enough_data_response)
            else:
                self.assertEqual(db_count, response_obj['count'])

    def test_public_filtering_extra_properties_range_string_2(self):
        # extra_properties range search (both min and max ranges) and extra_properties string search (single value)
        response = self.client.get(
            '/api/public?extra_properties=[{"lab_test_result_value": {"rangeMin": 5, "rangeMax": 900}}, '
            '{"covidstatus": "positive"}]'
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        response_obj = response.json()
        # if there is no CONFIG file then the response_obj count is count of all because the filter is ignored
        range_parameters = {
            "extra_properties__lab_test_result_value__gte": 5,
            "extra_properties__lab_test_result_value__lte": 900,
            "extra_properties__covidstatus__icontains": "positive",
        }
        db_count = Individual.objects.filter(**range_parameters).count()
        if CONFIG_FIELDS:
            self.assertIn(self.response_threshold_check(response_obj), [db_count, self.not_enough_data_response])
            if db_count <= self.response_threshold:
                self.assertEqual(response_obj, self.not_enough_data_response)
            else:
                self.assertEqual(db_count, response_obj['count'])

    def test_public_filtering_extra_properties_range_string_3(self):
        # extra_properties range search (only max range) and extra_properties string search (multiple values)
        response = self.client.get(
            '/api/public?extra_properties=[{"lab_test_result_value": {"rangeMax": 400}}, '
            '{"covidstatus": "positive"}, {"smoking": "Non-smoker"}]'
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        response_obj = response.json()
        # if there is no CONFIG file then the response_obj count is count of all because the filter is ignored
        range_parameters = {
            "extra_properties__lab_test_result_value__lte": 400,
            "extra_properties__covidstatus__icontains": "positive",
            "extra_properties__smoking__icontains": "Non-smoker",
        }
        db_count = Individual.objects.filter(**range_parameters).count()
        if CONFIG_FIELDS:
            self.assertIn(self.response_threshold_check(response_obj), [db_count, self.not_enough_data_response])
            if db_count <= self.response_threshold:
                self.assertEqual(response_obj, self.not_enough_data_response)
            else:
                self.assertEqual(db_count, response_obj['count'])

    def test_public_filtering_extra_properties_multiple_ranges_1(self):
        # extra_properties range search (both min and max range, multiple values)
        response = self.client.get(
            '/api/public?extra_properties=[{"lab_test_result_value": {"rangeMin": 5, "rangeMax": 900}}, '
            '{"baseline_creatinine": {"rangeMin": 30, "rangeMax": 300}}]'
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        response_obj = response.json()
        # if there is no CONFIG file then the response_obj count is count of all because the filter is ignored
        range_parameters = {
            "extra_properties__lab_test_result_value__gte": 5,
            "extra_properties__lab_test_result_value__lte": 900,
            "extra_properties__baseline_creatinine__gte": 30,
            "extra_properties__baseline_creatinine__lte": 300,
        }
        db_count = Individual.objects.filter(**range_parameters).count()
        if CONFIG_FIELDS:
            self.assertIn(self.response_threshold_check(response_obj), [db_count, self.not_enough_data_response])
            if db_count <= self.response_threshold:
                self.assertEqual(response_obj, self.not_enough_data_response)
            else:
                self.assertEqual(db_count, response_obj['count'])

    def test_public_filtering_extra_properties_multiple_ranges_2(self):
        # extra_properties range search (only min or max range, multiple values)
        response = self.client.get(
            '/api/public?extra_properties=[{"lab_test_result_value": {"rangeMin": 5}}, '
            '{"baseline_creatinine": {"rangeMax": 300}}]'
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        response_obj = response.json()
        # if there is no CONFIG file then the response_obj count is count of all because the filter is ignored
        range_parameters = {
            "extra_properties__lab_test_result_value__gte": 5,
            "extra_properties__baseline_creatinine__lte": 300,
        }
        db_count = Individual.objects.filter(**range_parameters).count()
        if CONFIG_FIELDS:
            self.assertIn(self.response_threshold_check(response_obj), [db_count, self.not_enough_data_response])
            if db_count <= self.response_threshold:
                self.assertEqual(response_obj, self.not_enough_data_response)
            else:
                self.assertEqual(db_count, response_obj['count'])
