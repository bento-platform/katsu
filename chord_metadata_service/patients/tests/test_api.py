import json
import csv
import io
from django.conf import settings
from django.urls import reverse
from django.test import override_settings
from rest_framework import status
from rest_framework.test import APITestCase
from chord_metadata_service.patients.models import Individual
from chord_metadata_service.restapi.tests.constants import CONFIG_PUBLIC_TEST, CONFIG_PUBLIC_TEST_SEARCH_SEX_ONLY
from chord_metadata_service.restapi.utils import iso_duration_to_years

from . import constants as c


class CreateIndividualTest(APITestCase):
    """ Test module for creating an Individual. """

    def setUp(self):

        self.valid_payload = c.VALID_INDIVIDUAL
        self.invalid_payload = c.INVALID_INDIVIDUAL

    def test_create_individual(self):
        """ POST a new individual. """

        response = self.client.post(
            reverse('individuals-list'),
            data=json.dumps(self.valid_payload),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Individual.objects.count(), 1)
        self.assertEqual(Individual.objects.get().id, 'patient:1')

    def test_create_invalid_individual(self):
        """ POST a new individual with invalid data. """

        invalid_response = self.client.post(
            reverse('individuals-list'),
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
                'individuals-detail',
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
                'individuals-detail',
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
                'individuals-detail',
                kwargs={'pk': self.individual_one.id}
            )
        )
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    def test_delete_non_existing_individual(self):
        """ DELETE a non-existing Individual record. """

        response = self.client.delete(
            reverse(
                'individuals-detail',
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


# Note: the next five tests use the same setUp method. Initially they were
# all combined in the same class. But this caused bugs with regard to unavailable
# postgre cursor in the call to `setUp()` after the first invocation for undetermined reasons.
# One hypothesis is that using POST requests without actually
# adding data to the database creates unexpected behaviour with one of the
# libraries used  during the testing (?) maybe at teardown time.
class BatchIndividualsCSVTest(APITestCase):
    """ Test for getting a batch of individuals as csv. """

    def setUp(self):
        self.individual_one = Individual.objects.create(**c.VALID_INDIVIDUAL)
        self.individual_two = Individual.objects.create(**c.VALID_INDIVIDUAL_2)

    def test_batch_individuals_csv_no_ids(self):
        data = json.dumps({'format': 'csv'})
        response = self.client.post(reverse('batch/individuals'), data, content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)


class BatchIndividualsCSVTest1(APITestCase):
    """ Test for getting a batch of individuals as csv. """

    def setUp(self):
        self.individual_one = Individual.objects.create(**c.VALID_INDIVIDUAL)
        self.individual_two = Individual.objects.create(**c.VALID_INDIVIDUAL_2)

    def test_batch_individuals_csv(self):
        data = json.dumps({'format': 'csv', 'id': [self.individual_one.id, self.individual_two.id]})
        get_resp = self.client.post(reverse('batch/individuals'), data, content_type='application/json')
        self.assertEqual(get_resp.status_code, status.HTTP_200_OK)

        content = get_resp.content.decode('utf-8')
        resp_csv_reader = csv.reader(io.StringIO(content))
        resp_body = list(resp_csv_reader)
        correct_content = f"{c.CSV_HEADER}\n{c.INDIVIDUAL_1_CSV}\n{c.INDIVIDUAL_2_CSV}"
        correct_csv_reader = csv.reader(io.StringIO(correct_content))
        correct_body = list(correct_csv_reader)
        self.assertEqual(resp_body[0], correct_body[0])
        for i in range(1, len(resp_body)):
            # last 2 columns are dates with a specific formating. We ignore those in the test by slicing
            self.assertEqual(resp_body[i][:-2], correct_body[i][:-2])


class BatchIndividualsCSVTest2(APITestCase):
    """ Test for getting a batch of individuals as csv. """

    def setUp(self):
        self.individual_one = Individual.objects.create(**c.VALID_INDIVIDUAL)
        self.individual_two = Individual.objects.create(**c.VALID_INDIVIDUAL_2)

    def test_batch_individuals_csv_invalid_ids(self):
        data = json.dumps({'format': 'csv', 'id': ['invalid']})
        response = self.client.post(reverse('batch/individuals'), data, content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)


class BatchIndividualsCSVTest3(APITestCase):
    """ Test for getting a batch of individuals as csv. """

    def setUp(self):
        self.individual_one = Individual.objects.create(**c.VALID_INDIVIDUAL)
        self.individual_two = Individual.objects.create(**c.VALID_INDIVIDUAL_2)

    def test_batch_individuals_csv_invalid_ids(self):
        data = json.dumps({'format': 'csv', 'id': [self.individual_one.id, 'invalid', "I don't exist"]})
        response = self.client.post(reverse('batch/individuals'), data, content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        lines = response.content.decode('utf8').split('\n')
        nb_lines = len([line for line in lines if line])    # ignore trailing line break
        self.assertEqual(nb_lines, 2)   # 2 lines expected: header + individual_one


class BatchIndividualsCSVTest4(APITestCase):
    """ Test for getting a batch of individuals as csv. """

    def setUp(self):
        self.individual_one = Individual.objects.create(**c.VALID_INDIVIDUAL)
        self.individual_two = Individual.objects.create(**c.VALID_INDIVIDUAL_2)

    def test_batch_individuals_csv_invalid_format(self):
        # defaults to default renderer
        data = json.dumps({'format': 'invalid', 'id': [self.individual_one.id]})
        response = self.client.post(reverse('batch/individuals'), data, content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)


class PublicListIndividualsTest(APITestCase):
    """ Test for api/public GET all """

    response_threshold = 5
    random_range = 137

    @staticmethod
    def response_threshold_check(response):
        return response['count'] if 'count' in response else settings.INSUFFICIENT_DATA_AVAILABLE

    def setUp(self):
        individuals = [c.generate_valid_individual() for _ in range(self.random_range)]  # random range
        for individual in individuals:
            Individual.objects.create(**individual)

    @override_settings(CONFIG_PUBLIC=CONFIG_PUBLIC_TEST)
    def test_public_get(self):
        # no filters GET request to /api/public, returns count or INSUFFICIENT_DATA_AVAILABLE
        response = self.client.get('/api/public')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        response_obj = response.json()
        self.assertIn(
            self.response_threshold_check(response_obj),
            [Individual.objects.all().count(), settings.INSUFFICIENT_DATA_AVAILABLE]
        )
        if Individual.objects.all().count() <= self.response_threshold:
            self.assertEqual(response_obj, settings.INSUFFICIENT_DATA_AVAILABLE)
        else:
            self.assertEqual(Individual.objects.all().count(), response_obj['count'])

    @override_settings(CONFIG_PUBLIC={})
    def test_public_get_no_config(self):
        # no filters GET request to /api/public when config is not provided, returns NO_PUBLIC_DATA_AVAILABLE
        response = self.client.get('/api/public')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        response_obj = response.json()
        self.assertIsInstance(response_obj, dict)
        self.assertEqual(response_obj, settings.NO_PUBLIC_DATA_AVAILABLE)


class PublicFilteringIndividualsTest(APITestCase):
    """ Test for api/public GET filtering """

    response_threshold = CONFIG_PUBLIC_TEST["rules"]["count_threshold"]
    random_range = 137

    @staticmethod
    def response_threshold_check(response):
        return response['count'] if 'count' in response else settings.INSUFFICIENT_DATA_AVAILABLE

    def setUp(self):
        individuals = [c.generate_valid_individual() for _ in range(self.random_range)]  # random range
        for individual in individuals:
            Individual.objects.create(**individual)

    @override_settings(CONFIG_PUBLIC=CONFIG_PUBLIC_TEST)
    def test_public_filtering_sex(self):
        # sex field search
        response = self.client.get('/api/public?sex=female')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        response_obj = response.json()
        nb_female = Individual.objects.filter(sex__iexact='female').count()
        self.assertIn(
            self.response_threshold_check(response_obj),
            [nb_female, settings.INSUFFICIENT_DATA_AVAILABLE]
        )
        if nb_female <= self.response_threshold:
            self.assertEqual(response_obj, settings.INSUFFICIENT_DATA_AVAILABLE)
        else:
            self.assertEqual(nb_female, response_obj['count'])

    @override_settings(CONFIG_PUBLIC=CONFIG_PUBLIC_TEST)
    def test_public_filtering_2_fields(self):
        # sex and extra_properties string search
        # test GET query string search for extra_properties field
        response = self.client.get('/api/public?sex=female&smoking=Smoker')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        response_obj = response.json()
        db_count = Individual.objects.filter(sex__iexact='female')\
            .filter(extra_properties__contains={"smoking": "Smoker"}).count()
        self.assertIn(self.response_threshold_check(response_obj), [db_count, settings.INSUFFICIENT_DATA_AVAILABLE])
        if db_count <= self.response_threshold:
            self.assertEqual(response_obj, settings.INSUFFICIENT_DATA_AVAILABLE)
        else:
            self.assertEqual(db_count, response_obj['count'])

    # test the same as above but with an empty CONFIG_PUBLIC
    @override_settings(CONFIG_PUBLIC={})
    def test_public_filtering_2_fields_config_empty(self):
        # sex and extra_properties string search
        # test GET query string search for extra_properties field
        response = self.client.get('/api/public?sex=female&smoking=Non-smoker')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        response_obj = response.json()
        self.assertIsInstance(response_obj, dict)
        self.assertEqual(response_obj, settings.NO_PUBLIC_DATA_AVAILABLE)

    @override_settings(CONFIG_PUBLIC=CONFIG_PUBLIC_TEST)
    def test_public_filtering_extra_properties_1(self):
        # extra_properties string search (multiple values)
        response = self.client.get('/api/public?smoking=Non-smoker&death_dc=Deceased')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        response_obj = response.json()
        db_count = Individual.objects.filter(
            extra_properties__contains={"smoking": "Non-smoker", "death_dc": "Deceased"}
        ).count()
        self.assertIn(self.response_threshold_check(response_obj), [db_count, settings.INSUFFICIENT_DATA_AVAILABLE])
        if db_count <= self.response_threshold:
            self.assertEqual(response_obj, settings.INSUFFICIENT_DATA_AVAILABLE)
        else:
            self.assertEqual(db_count, response_obj['count'])

    # test the same as above but with an empty CONFIG_PUBLIC
    @override_settings(CONFIG_PUBLIC={})
    def test_public_filtering_extra_properties_1_config_empty(self):
        # extra_properties string search
        # test GET query string search for extra_properties field
        response = self.client.get('/api/public?smoking=Non-smoker&death_dc=Deceased')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        response_obj = response.json()
        self.assertIsInstance(response_obj, dict)
        self.assertEqual(response_obj, settings.NO_PUBLIC_DATA_AVAILABLE)

    @override_settings(CONFIG_PUBLIC=CONFIG_PUBLIC_TEST)
    def test_public_filtering_extra_properties_2(self):
        # extra_properties string search (multiple values)
        response = self.client.get(
            '/api/public?smoking=Non-smoker&death_dc=deceased&covidstatus=positive'
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        response_obj = response.json()
        self.assertEqual(response_obj["code"], 400)

    @override_settings(CONFIG_PUBLIC=CONFIG_PUBLIC_TEST)
    def test_public_filtering_extra_properties_invalid_3(self):
        # if GET query string list has various data types Error
        response = self.client.get('/api/public?extra_properties=[{"smoking": "Non-smoker"}, 5, "Test"]')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        response_obj = response.json()
        self.assertEqual(response_obj["code"], 400)

    @override_settings(CONFIG_PUBLIC=CONFIG_PUBLIC_TEST)
    def test_public_filtering_extra_properties_range_1(self):
        # extra_properties range search (both min and max ranges, single value)
        response = self.client.get(
            '/api/public?lab_test_result_value=50-100'
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        response_obj = response.json()
        range_parameters = {
            "extra_properties__lab_test_result_value__gte": 50,
            "extra_properties__lab_test_result_value__lt": 100
        }
        db_count = Individual.objects.filter(**range_parameters).count()
        self.assertIn(self.response_threshold_check(response_obj), [db_count, settings.INSUFFICIENT_DATA_AVAILABLE])
        if db_count <= self.response_threshold:
            self.assertEqual(response_obj, settings.INSUFFICIENT_DATA_AVAILABLE)
        else:
            self.assertEqual(db_count, response_obj['count'])

    @override_settings(CONFIG_PUBLIC=CONFIG_PUBLIC_TEST)
    def test_public_filtering_extra_properties_range_2(self):
        # extra_properties range search (above taper, single value)
        response = self.client.get(
            '/api/public?baseline_creatinine=≥ 200'
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        response_obj = response.json()
        range_parameters = {
            "extra_properties__baseline_creatinine__gte": 200,
        }
        db_count = Individual.objects.filter(**range_parameters).count()
        self.assertIn(self.response_threshold_check(response_obj), [db_count, settings.INSUFFICIENT_DATA_AVAILABLE])
        if db_count <= self.response_threshold:
            self.assertEqual(response_obj, settings.INSUFFICIENT_DATA_AVAILABLE)
        else:
            self.assertEqual(db_count, response_obj['count'])

    @override_settings(CONFIG_PUBLIC=CONFIG_PUBLIC_TEST)
    def test_public_filtering_extra_properties_range_3(self):
        # extra_properties range search (below taper, single value)
        response = self.client.get(
            '/api/public?baseline_creatinine=< 50'
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        response_obj = response.json()
        range_parameters = {
            "extra_properties__baseline_creatinine__lt": 50,
        }
        db_count = Individual.objects.filter(**range_parameters).count()
        self.assertIn(self.response_threshold_check(response_obj), [db_count, settings.INSUFFICIENT_DATA_AVAILABLE])
        if db_count <= self.response_threshold:
            self.assertEqual(response_obj, settings.INSUFFICIENT_DATA_AVAILABLE)
        else:
            self.assertEqual(db_count, response_obj['count'])

    @override_settings(CONFIG_PUBLIC=CONFIG_PUBLIC_TEST)
    def test_public_filtering_extra_properties_wrong_range(self):
        # extra_properties range search, unauthorized range
        response = self.client.get(
            '/api/public?lab_test_result_value=100-200'
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        response_obj = response.json()
        self.assertEqual(response_obj["code"], 400)

    @override_settings(CONFIG_PUBLIC=CONFIG_PUBLIC_TEST)
    def test_public_filtering_extra_properties_range_string_1(self):
        # sex string search and extra_properties range search
        response = self.client.get(
            '/api/public?sex=female&lab_test_result_value=100-150'
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        response_obj = response.json()
        range_parameters = {
            "sex__iexact": "female",
            "extra_properties__lab_test_result_value__gte": 100,
            "extra_properties__lab_test_result_value__lt": 150
        }
        db_count = Individual.objects.filter(**range_parameters).count()
        self.assertIn(self.response_threshold_check(response_obj), [db_count, settings.INSUFFICIENT_DATA_AVAILABLE])
        if db_count <= self.response_threshold:
            self.assertEqual(response_obj, settings.INSUFFICIENT_DATA_AVAILABLE)
        else:
            self.assertEqual(db_count, response_obj['count'])

    @override_settings(CONFIG_PUBLIC=CONFIG_PUBLIC_TEST)
    def test_public_filtering_extra_properties_range_string_2(self):
        # extra_properties range search (both min and max ranges) and extra_properties string search (single value)
        response = self.client.get(
            '/api/public?lab_test_result_value=100-150&covidstatus=positive'
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        response_obj = response.json()
        range_parameters = {
            "extra_properties__lab_test_result_value__gte": 100,
            "extra_properties__lab_test_result_value__lt": 150,
            "extra_properties__covidstatus__iexact": "positive",
        }
        db_count = Individual.objects.filter(**range_parameters).count()
        self.assertIn(self.response_threshold_check(response_obj), [db_count, settings.INSUFFICIENT_DATA_AVAILABLE])
        if db_count <= self.response_threshold:
            self.assertEqual(response_obj, settings.INSUFFICIENT_DATA_AVAILABLE)
        else:
            self.assertEqual(db_count, response_obj['count'])

    @override_settings(CONFIG_PUBLIC=CONFIG_PUBLIC_TEST)
    def test_public_filtering_extra_properties_multiple_ranges_1(self):
        # extra_properties range search (both min and max range, multiple values)
        response = self.client.get(
            '/api/public?lab_test_result_value=100-150&baseline_creatinine=100-150'
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        response_obj = response.json()
        range_parameters = {
            "extra_properties__lab_test_result_value__gte": 100,
            "extra_properties__lab_test_result_value__lt": 150,
            "extra_properties__baseline_creatinine__gte": 100,
            "extra_properties__baseline_creatinine__lt": 150,
        }
        db_count = Individual.objects.filter(**range_parameters).count()
        self.assertIn(self.response_threshold_check(response_obj), [db_count, settings.INSUFFICIENT_DATA_AVAILABLE])
        if db_count <= self.response_threshold:
            self.assertEqual(response_obj, settings.INSUFFICIENT_DATA_AVAILABLE)
        else:
            self.assertEqual(db_count, response_obj['count'])

    @override_settings(CONFIG_PUBLIC=CONFIG_PUBLIC_TEST)
    def test_public_filtering_extra_properties_date_range_1(self):
        # extra_properties date range search (only after or before, single value)
        response = self.client.get(
            '/api/public?date_of_consent=Mar 2021'
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        response_obj = response.json()
        range_parameters = {
            "extra_properties__date_of_consent__startswith": "2021-03"
        }
        db_count = Individual.objects.filter(**range_parameters).count()
        self.assertIn(self.response_threshold_check(response_obj), [db_count, settings.INSUFFICIENT_DATA_AVAILABLE])
        if db_count <= self.response_threshold:
            self.assertEqual(response_obj, settings.INSUFFICIENT_DATA_AVAILABLE)
        else:
            self.assertEqual(db_count, response_obj['count'])

    @override_settings(CONFIG_PUBLIC=CONFIG_PUBLIC_TEST)
    def test_public_filtering_extra_properties_date_range_and_other_range(self):
        # extra_properties date range search (both after and before, single value) and other number range search
        response = self.client.get(
            '/api/public?date_of_consent=Mar 2021&lab_test_result_value=100-150'
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        response_obj = response.json()
        range_parameters = {
            "extra_properties__date_of_consent__startswith": "2021-03",
            "extra_properties__lab_test_result_value__gte": 100,
            "extra_properties__lab_test_result_value__lt": 150,
        }
        db_count = Individual.objects.filter(**range_parameters).count()
        self.assertIn(self.response_threshold_check(response_obj), [db_count, settings.INSUFFICIENT_DATA_AVAILABLE])
        if db_count <= self.response_threshold:
            self.assertEqual(response_obj, settings.INSUFFICIENT_DATA_AVAILABLE)
        else:
            self.assertEqual(db_count, response_obj['count'])


class PublicAgeRangeFilteringIndividualsTest(APITestCase):
    """ Test for api/public GET filtering """

    response_threshold = 5
    random_range = 45

    @staticmethod
    def response_threshold_check(response):
        return response['count'] if 'count' in response else settings.INSUFFICIENT_DATA_AVAILABLE

    def setUp(self):
        individuals = [c.generate_valid_individual() for _ in range(self.random_range)]  # random range
        for individual in individuals:
            Individual.objects.create(**individual)

        for individual in Individual.objects.all():
            if individual.age:
                if "age" in individual.age:
                    age_numeric, age_unit = iso_duration_to_years(individual.age["age"])
                    individual.age_numeric = age_numeric
                    individual.age_unit = age_unit if age_unit else ""
                    individual.save()

    @override_settings(CONFIG_PUBLIC=CONFIG_PUBLIC_TEST)
    def test_public_filtering_age_range(self):
        # age valid range search
        response = self.client.get('/api/public?age=20-30')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        response_obj = response.json()
        db_count = Individual.objects.filter(age_numeric__gte=20, age_numeric__lt=30).count()
        self.assertIn(self.response_threshold_check(response_obj), [db_count, settings.INSUFFICIENT_DATA_AVAILABLE])
        if db_count <= self.response_threshold:
            self.assertEqual(response_obj, settings.INSUFFICIENT_DATA_AVAILABLE)
        else:
            self.assertEqual(db_count, response_obj['count'])

    @override_settings(CONFIG_PUBLIC=CONFIG_PUBLIC_TEST)
    def test_public_filtering_age_invalid_range(self):
        # age invalid range max search
        response = self.client.get('/api/public?age=10-50')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        response_obj = response.json()
        self.assertEqual(response_obj["code"], 400)

    @override_settings(CONFIG_PUBLIC=CONFIG_PUBLIC_TEST_SEARCH_SEX_ONLY)
    def test_public_filtering_age_range_min_and_max_no_age_in_config(self):
        # test with config without age field, returns error
        response = self.client.get('/api/public?age=20-30')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        response_obj = response.json()
        self.assertEqual(response_obj["code"], 400)

    @override_settings(CONFIG_PUBLIC={})
    def test_public_filtering_age_range_min_and_max_no_config(self):
        # test when config is not provided, returns NO_PUBLIC_DATA_AVAILABLE
        response = self.client.get('/api/public?age=20-30')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        response_obj = response.json()
        self.assertIsInstance(response_obj, dict)
        self.assertIsInstance(response_obj, dict)
        self.assertEqual(response_obj, settings.NO_PUBLIC_DATA_AVAILABLE)
