import csv
import io
import random
import uuid

from bento_lib.discovery import DiscoveryConfig
from copy import deepcopy

from django.db.models import Q
from django.urls import reverse
from django.test import TestCase, override_settings
from rest_framework import status
from chord_metadata_service.authz.tests.helpers import AuthzAPITestCase
from chord_metadata_service.chord import models as cm
from chord_metadata_service.chord.tests.constants import VALID_DATA_USE_1
from chord_metadata_service.chord.tests.helpers import ProjectTestCase
from chord_metadata_service.discovery import responses as dres
from chord_metadata_service.discovery.tests.constants import (
    DISCOVERY_CONFIG_EXTRA_PROPERTIES,
    DISCOVERY_CONFIG_TEST,
    CONFIG_PUBLIC_TEST_SEARCH_SEX_ONLY,
    DISCOVERY_ZERO_COUNTS,
)
from chord_metadata_service.experiments import models as ex_m
from chord_metadata_service.experiments.tests import constants as ex_c
from chord_metadata_service.patients.models import Individual, VitalStatus
from chord_metadata_service.phenopackets import models as ph_m
from chord_metadata_service.phenopackets.tests import constants as ph_c
from chord_metadata_service.phenopackets.utils import iso_duration_to_years
from chord_metadata_service.restapi.api_renderers import render_age

from . import constants as c

CONFIG_PUBLIC_TEST_NO_THRESHOLD: DiscoveryConfig = deepcopy(DISCOVERY_CONFIG_TEST)
CONFIG_PUBLIC_TEST_NO_THRESHOLD.rules.count_threshold = 0


class CreateIndividualTest(AuthzAPITestCase):
    """ Test module for creating an Individual. """

    def setUp(self):

        self.valid_payload = c.VALID_INDIVIDUAL
        self.invalid_payload = c.INVALID_INDIVIDUAL

        self.maxDiff = None

    @staticmethod
    def _without_timestamps(x: dict) -> dict:
        y = {**x}
        del y["created"]
        del y["updated"]
        return y

    def test_create_individual(self):
        """ POST a new individual. """

        response = self.one_authz_post(reverse('individuals-list'), json=self.valid_payload)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Individual.objects.count(), 1)
        self.assertEqual(Individual.objects.get().id, 'patient:1')

        response = self.one_authz_get(reverse('individuals-detail', kwargs={'pk': 'patient:1'}))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        rhs = {
            **self.valid_payload,
            "karyotypic_sex": "UNKNOWN_KARYOTYPE",  # default value
        }
        self.assertDictEqual(self._without_timestamps(response.json()), rhs)

    def test_create_individual_no_vital_status(self):
        """ POST a new individual without a vital status. """

        vp = {**self.valid_payload}
        del vp["vital_status"]
        response = self.one_authz_post(reverse('individuals-list'), json=vp)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Individual.objects.count(), 1)
        self.assertEqual(Individual.objects.get().id, 'patient:1')

        response = self.one_authz_get(reverse('individuals-detail', kwargs={'pk': 'patient:1'}))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        rhs = {
            **vp,
            "karyotypic_sex": "UNKNOWN_KARYOTYPE",  # default value
        }
        self.assertDictEqual(self._without_timestamps(response.json()), rhs)

    def test_create_individual_forbidden(self):
        response = self.one_no_authz_post(reverse('individuals-list'), json=self.valid_payload)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_create_invalid_individual(self):
        """ POST a new individual with invalid data. """

        invalid_response = self.one_authz_post(reverse('individuals-list'), json=self.invalid_payload)
        self.assertEqual(invalid_response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(Individual.objects.count(), 0)


class TestWithIndividual(AuthzAPITestCase):
    def setUp(self):
        self.vital_status = VitalStatus.objects.create(**c.VALID_INDIVIDUAL["vital_status"])
        self.individual_one = Individual.objects.create(**{**c.VALID_INDIVIDUAL, "vital_status": self.vital_status})


class TestWithTwoIndividuals(TestWithIndividual):
    def setUp(self):
        super().setUp()
        # second individual without vital status
        self.individual_two = Individual.objects.create(**c.VALID_INDIVIDUAL_2)


class UpdateIndividualTest(TestWithIndividual):
    """ Test module for updating an existing Individual record. """

    put_valid_payload = {
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
    }

    invalid_payload = c.INVALID_INDIVIDUAL

    def test_update_individual(self):
        """ PUT new data in an existing Individual record. """

        response = self.one_authz_put(
            reverse('individuals-detail', kwargs={'pk': self.individual_one.id}),
            json=self.put_valid_payload
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_update_individual_forbidden(self):
        response = self.one_no_authz_put(
            reverse('individuals-detail', kwargs={'pk': self.individual_one.id}),
            json=self.put_valid_payload
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_update_invalid_individual(self):
        """ PUT new invalid data in an existing Individual record. """

        response = self.one_authz_put(
            reverse('individuals-detail', kwargs={'pk': self.individual_one.id}),
            json=self.invalid_payload,
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


class DeleteIndividualTest(TestWithIndividual):
    """ Test module for deleting an existing Individual record. """

    def test_delete_individual(self):
        """ DELETE an existing Individual record. """

        response = self.one_authz_delete(
            reverse('individuals-detail', kwargs={'pk': self.individual_one.id})
        )
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    def test_delete_individual_forbidden(self):
        response = self.one_no_authz_delete(
            reverse('individuals-detail', kwargs={'pk': self.individual_one.id})
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_delete_non_existing_individual(self):
        """ DELETE a non-existing Individual record. """

        response = self.one_authz_delete(
            reverse('individuals-detail', kwargs={'pk': 'patient:what'})
        )
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)


class IndividualListFilterTest(TestWithTwoIndividuals):

    def setUp(self):
        super().setUp()

        # ----

        self.project_1 = cm.Project.objects.create(title="Project 1", description="p1")
        self.dataset_1 = cm.Dataset.objects.create(**{
            "title": "Dataset 1",
            "description": "Test Dataset 1",
            "data_use": VALID_DATA_USE_1,
            "project": self.project_1
        })

        self.project_2 = cm.Project.objects.create(title="Project 2", description="p2")
        self.dataset_2 = cm.Dataset.objects.create(**{
            "title": "Dataset 2",
            "description": "Test Dataset 2",
            "data_use": VALID_DATA_USE_1,
            "project": self.project_2
        })

        # ----

        self.md1 = ph_m.MetaData.objects.create(**ph_c.VALID_META_DATA_1)

        self.pheno1 = ph_m.Phenopacket.objects.create(
            **ph_c.valid_phenopacket(self.individual_one, self.md1, "phenopacket:1")
        )
        self.pheno1.dataset = self.dataset_1
        self.pheno1.save()

        self.pheno2 = ph_m.Phenopacket.objects.create(
            **ph_c.valid_phenopacket(self.individual_two, self.md1, "phenopacket:2")
        )
        self.pheno2.dataset = self.dataset_2
        self.pheno2.save()

    def test_individuals_list(self):
        r = self.one_authz_get("/api/individuals")
        data = r.json()
        self.assertEqual(len(data["results"]), 2)

    def test_individuals_project_scope(self):
        r = self.one_authz_get(f"/api/individuals?project={self.project_1.identifier}")
        data = r.json()
        self.assertEqual(len(data["results"]), 1)
        self.assertEqual(data["results"][0]["id"], self.individual_one.id)

        r = self.one_authz_get(f"/api/individuals?project={self.project_2.identifier}")
        data = r.json()
        self.assertEqual(len(data["results"]), 1)
        self.assertEqual(data["results"][0]["id"], self.individual_two.id)

    def test_individuals_dataset_scope(self):
        r = self.one_authz_get(
            f"/api/individuals?project={self.project_1.identifier}&dataset={self.dataset_1.identifier}"
        )
        data = r.json()
        self.assertEqual(len(data["results"]), 1)
        self.assertEqual(data["results"][0]["id"], self.individual_one.id)

        r = self.one_authz_get(
            f"/api/individuals?project={self.project_2.identifier}&dataset={self.dataset_2.identifier}"
        )
        data = r.json()
        self.assertEqual(len(data["results"]), 1)
        self.assertEqual(data["results"][0]["id"], self.individual_two.id)

    def test_individuals_forbidden(self):
        r = self.one_no_authz_get("/api/individuals")
        self.assertEqual(r.status_code, status.HTTP_403_FORBIDDEN)

        r = self.one_no_authz_get(f"/api/individuals?project={self.project_1.identifier}")
        self.assertEqual(r.status_code, status.HTTP_403_FORBIDDEN)


class IndividualCSVRendererTest(TestWithIndividual):
    """ Test csv export for Individuals. """

    def test_csv_export(self):
        get_resp = self.one_authz_get('/api/individuals?format=csv')
        self.assertEqual(get_resp.status_code, status.HTTP_200_OK)
        content = get_resp.content.decode('utf-8')
        cvs_reader = csv.reader(io.StringIO(content))
        body = list(cvs_reader)
        self.assertEqual(body[1][1], c.VALID_INDIVIDUAL['sex'])
        headers = body.pop(0)
        for column in ['id', 'sex', 'date of birth', 'taxonomy', 'karyotypic sex',
                       'age', 'diseases', 'created', 'updated']:
            self.assertIn(column, [column_name.lower() for column_name in headers])

    def test_csv_export_forbidden(self):
        get_resp = self.one_no_authz_get('/api/individuals?format=csv')
        self.assertEqual(get_resp.status_code, status.HTTP_403_FORBIDDEN)


class IndividualWithPhenopacketSearchTest(TestWithTwoIndividuals):
    """ Test for api/individuals?search= """

    # params, expected # results, expected result object # keys
    search_test_params = (
        ("search=P49Y", 1, None),
        ("search=NCBITaxon:9606", 2, None),
        # 8 fields in the individuals Bento search response
        # (original Bento search response + dataset/project/phenopacket IDs):
        #  - subject_id
        #  - dataset_id
        #  - project_id
        #  - phenopacket_id
        #  - alternate_ids
        #  - num_experiments
        #  - biosamples
        #  - experiments_with_biosamples
        # only 1 of the individuals has any phenopackets (2):
        ("search=P49Y&format=bento_search_result", 2, 8),
        ("search=NCBITaxon:9606&format=bento_search_result", 2, 8),
    )

    def setUp(self):
        super().setUp()

        self.metadata_1 = ph_m.MetaData.objects.create(**ph_c.VALID_META_DATA_1)
        self.phenopacket_1 = ph_m.Phenopacket.objects.create(
            **ph_c.valid_phenopacket(subject=self.individual_one, meta_data=self.metadata_1)
        )
        self.phenopacket_2 = ph_m.Phenopacket.objects.create(
            **ph_c.valid_phenopacket(subject=self.individual_one, meta_data=self.metadata_1, id="phenopacket:2")
        )

    def test_search(self):  # test full-text search (standard + bento search format)
        for params in self.search_test_params:
            with self.subTest(params=params):
                res = self.one_authz_get(f"/api/individuals?{params[0]}")
                self.assertEqual(res.status_code, status.HTTP_200_OK)
                res_data = res.json()
                self.assertEqual(len(res_data["results"]), params[1])
                if (n_keys := params[2]) is not None:
                    self.assertEqual(len(res_data["results"][0]), n_keys)

    def test_search_forbidden(self):
        for params in self.search_test_params:
            with self.subTest(params=params):
                res = self.one_no_authz_get(f"/api/individuals?{params[0]}")
                self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)

    def test_individual_phenopackets(self):
        get_resp = self.one_authz_get(f"/api/individuals/{self.individual_one.id}/phenopackets")
        self.assertEqual(get_resp.status_code, status.HTTP_200_OK)
        response_obj_1 = get_resp.json()
        self.assertEqual(len(response_obj_1), 2)  # 2 phenopackets for individual

    def test_individual_phenopackets_forbidden(self):
        get_resp = self.one_no_authz_get(f"/api/individuals/{self.individual_one.id}/phenopackets")
        self.assertEqual(get_resp.status_code, status.HTTP_403_FORBIDDEN)

    def test_individual_phenopackets_attachment(self):
        post_resp = self.one_authz_post(f"/api/individuals/{self.individual_one.id}/phenopackets?attachment=1")
        self.assertEqual(post_resp.status_code, status.HTTP_200_OK)
        self.assertIn("attachment; filename=", post_resp.headers.get("Content-Disposition", ""))
        response_obj_2 = post_resp.json()
        self.assertEqual(len(response_obj_2), 2)  # 2 phenopackets for individual, still

    def test_individual_phenopackets_attachment_forbidden(self):
        post_resp = self.one_no_authz_post(f"/api/individuals/{self.individual_one.id}/phenopackets?attachment=1")
        self.assertEqual(post_resp.status_code, status.HTTP_403_FORBIDDEN)


# Note: the next five tests use the same setUp method. Initially they were
# all combined in the same class. But this caused bugs with regard to unavailable
# postgre cursor in the call to `setUp()` after the first invocation for undetermined reasons.
# One hypothesis is that using POST requests without actually
# adding data to the database creates unexpected behaviour with one of the
# libraries used  during the testing (?) maybe at teardown time.
class BatchIndividualsCSVTest(TestWithTwoIndividuals):
    """ Test for getting a batch of individuals as csv. """

    def test_batch_individuals_csv_no_ids(self):
        response = self.one_authz_post(reverse('batch/individuals'), json={'format': 'csv'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_batch_individuals_csv_forbidden(self):
        response = self.one_no_authz_post(reverse('batch/individuals'), json={'format': 'csv'})
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)


class BatchIndividualsCSVTest1(TestWithTwoIndividuals):
    """ Test for getting a batch of individuals as csv. """

    def test_batch_individuals_csv(self):
        get_resp = self.one_authz_post(
            reverse('batch/individuals'),
            json={'format': 'csv', 'id': [self.individual_one.id, self.individual_two.id]}
        )
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


class BatchIndividualsCSVTest2(TestWithTwoIndividuals):
    """ Test for getting a batch of individuals as csv. """

    def test_batch_individuals_csv_invalid_ids(self):
        response = self.one_authz_post(reverse('batch/individuals'), json={'format': 'csv', 'id': ['invalid']})
        self.assertEqual(response.status_code, status.HTTP_200_OK)


class BatchIndividualsCSVTest3(TestWithTwoIndividuals):
    """ Test for getting a batch of individuals as csv. """

    def test_batch_individuals_csv_invalid_ids(self):
        response = self.one_authz_post(
            reverse('batch/individuals'),
            json={'format': 'csv', 'id': [self.individual_one.id, 'invalid', "I don't exist"]},
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        lines = response.content.decode('utf8').split('\n')
        nb_lines = len([line for line in lines if line])    # ignore trailing line break
        self.assertEqual(nb_lines, 2)   # 2 lines expected: header + individual_one


class BatchIndividualsCSVTest4(TestWithTwoIndividuals):
    """ Test for getting a batch of individuals as csv. """

    def test_batch_individuals_csv_invalid_format(self):
        # defaults to default renderer
        response = self.one_authz_post(
            reverse('batch/individuals'), json={'format': 'invalid', 'id': [self.individual_one.id]})
        self.assertEqual(response.status_code, status.HTTP_200_OK)


class PublicListIndividualsTest(AuthzAPITestCase):
    """ Test for api/public GET all """

    random_range = 137

    @staticmethod
    def response_threshold_check(response):
        return response["counts"]["individual"] if "counts" in response else dres.INSUFFICIENT_DATA_AVAILABLE

    def setUp(self):
        individuals = [c.generate_valid_individual() for _ in range(self.random_range)]  # random range
        for individual in individuals:
            Individual.objects.create(**individual)

    @override_settings(CONFIG_PUBLIC=DISCOVERY_CONFIG_TEST)
    def test_public_get(self):
        # no filters GET request to /api/public, returns count or INSUFFICIENT_DATA_AVAILABLE
        for fn_i, fn in enumerate((self.dt_authz_counts_get, self.dt_authz_full_get)):
            with self.subTest(params=(fn,)):
                response = fn("/api/public")
                self.assertEqual(response.status_code, status.HTTP_200_OK)
                response_obj = response.json()
                ind_count = Individual.objects.all().count()
                if fn_i == 0 and ind_count <= DISCOVERY_CONFIG_TEST.rules.count_threshold:
                    self.assertEqual(response_obj, dres.INSUFFICIENT_DATA_AVAILABLE)
                else:
                    self.assertEqual(Individual.objects.all().count(), response_obj['count'])
                    self.assertEqual(response_obj['biosamples']['count'], 0)
                    self.assertIsInstance(response_obj['biosamples']['sampled_tissue'], list)
                    self.assertEqual(response_obj['experiments']['count'], 0)
                    self.assertIsInstance(response_obj['experiments']['experiment_type'], list)

    @override_settings(CONFIG_PUBLIC=DiscoveryConfig())
    def test_public_get_no_config(self):
        # no filters GET request to /api/public when config is not provided, returns NO_PUBLIC_DATA_AVAILABLE
        response = self.dt_authz_counts_get('/api/public')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        response_obj = response.json()
        self.assertIsInstance(response_obj, dict)
        self.assertEqual(response_obj, dres.NO_PUBLIC_DATA_AVAILABLE)

    @override_settings(CONFIG_PUBLIC=DISCOVERY_CONFIG_TEST)
    def test_public_get_forbidden_none(self):
        r = self.dt_authz_none_get("/api/public")
        self.assertEqual(r.status_code, status.HTTP_403_FORBIDDEN)

    @override_settings(CONFIG_PUBLIC=DISCOVERY_CONFIG_TEST)
    def test_public_get_forbidden_bool(self):
        r = self.dt_authz_bool_get("/api/public")
        self.assertEqual(r.status_code, status.HTTP_403_FORBIDDEN)

    @override_settings(CONFIG_PUBLIC=DISCOVERY_CONFIG_TEST)
    def test_public_project_does_not_exist(self):
        r = self.dt_authz_counts_get(f"/api/public?project={uuid.uuid4()}")
        self.assertEqual(r.status_code, status.HTTP_404_NOT_FOUND)

    @override_settings(CONFIG_PUBLIC=DISCOVERY_CONFIG_TEST)
    def test_public_project_dataset_does_not_exist(self):
        r = self.dt_authz_counts_get(f"/api/public?project={uuid.uuid4()}&dataset={uuid.uuid4()}")
        self.assertEqual(r.status_code, status.HTTP_404_NOT_FOUND)


class DiscoveryFilteringIndividualsTest(AuthzAPITestCase, ProjectTestCase):
    """ Test for api/public GET filtering """

    response_threshold = DISCOVERY_CONFIG_TEST.rules.count_threshold
    num_individuals = 137
    random_seed = 341  # do not change this please :))

    @staticmethod
    def response_threshold_check(response):
        return response['count'] if 'count' in response else dres.INSUFFICIENT_DATA_AVAILABLE

    def setUp(self):
        self.project_2 = cm.Project.objects.create(title="Project 2", description="")
        self.dataset_2 = cm.Dataset.objects.create(
            title="Dataset 2",
            description="Some dataset",
            data_use=VALID_DATA_USE_1,
            project=self.project_2,
        )

        self.individuals = [
            c.generate_valid_individual(date_of_consent_range=(2020, 2023))
            for _ in range(self.num_individuals)
        ]

        individual_objs = [Individual.objects.create(**individual) for individual in self.individuals]
        biosample = ph_m.Biosample.objects.create(**ph_c.valid_biosample_1(individual_objs[0]))

        for idx, individual in enumerate(individual_objs, 1):
            meta_data = ph_m.MetaData.objects.create(**ph_c.VALID_META_DATA_1)
            phenopacket = ph_m.Phenopacket.objects.create(
                id=f"phenopacket_id:{idx}",
                subject=individual,
                meta_data=meta_data,
                dataset=self.dataset,
            )
            if idx == 1:
                phenopacket.biosamples.add(biosample)
                phenopacket.save()

                phenopacket_2 = ph_m.Phenopacket.objects.create(
                    id=f"phenopacket_id:{idx}-2",
                    subject=individual,
                    meta_data=meta_data,
                    dataset=self.dataset,
                )
                biosample_2 = ph_m.Biosample.objects.create(**ph_c.valid_biosample_2(individual))
                phenopacket_2.biosamples.add(biosample_2)
                phenopacket_2.save()
            else:  # in the discovery testing context, we need at least one phenopacket for the individuals
                phenopacket.save()

        instrument = ex_m.Instrument.objects.create(**ex_c.valid_instrument())
        ex_m.Experiment.objects.create(**ex_c.valid_experiment(biosample, instrument, self.dataset, 1))
        ex_m.Experiment.objects.create(**ex_c.valid_experiment(biosample, instrument, self.dataset, 2))

        random.seed(self.random_seed)

    @override_settings(CONFIG_PUBLIC=DISCOVERY_CONFIG_TEST)
    def test_discovery_filtering_sex(self):
        # sex field search
        response = self.dt_authz_counts_get('/api/discovery?sex=female')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        response_obj = response.json()
        nb_female = Individual.objects.filter(sex__iexact='female').count()
        self.assertIn(
            self.response_threshold_check(response_obj),
            [nb_female, dres.INSUFFICIENT_DATA_AVAILABLE]
        )
        self.assertEqual(response_obj["counts"]["individual"], 0 if nb_female <= self.response_threshold else nb_female)

    @override_settings(CONFIG_PUBLIC=DISCOVERY_CONFIG_TEST)
    def test_public_filtering_sex_none_in_project_counts(self):
        response = self.dt_authz_counts_get(f"/api/public?project={self.project_2.identifier}&sex=female")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.json(), dres.INSUFFICIENT_DATA_AVAILABLE)

        response = self.dt_authz_counts_get(
            f"/api/public?project={self.project_2.identifier}&dataset={self.dataset_2.identifier}&sex=female"
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.json(), dres.INSUFFICIENT_DATA_AVAILABLE)

    @override_settings(CONFIG_PUBLIC=DISCOVERY_CONFIG_TEST)
    def test_discovery_filtering_sex_none_in_project_counts(self):
        response = self.dt_authz_counts_get(f"/api/discovery?project={self.project_2.identifier}&sex=female")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.assertEqual(response.json()["counts"], DISCOVERY_ZERO_COUNTS)  # TODO: assert full empty response

        response = self.dt_authz_counts_get(
            f"/api/discovery?project={self.project_2.identifier}&dataset={self.dataset_2.identifier}&sex=female"
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.json()["counts"], DISCOVERY_ZERO_COUNTS)  # TODO: assert full empty response

    @override_settings(CONFIG_PUBLIC=DISCOVERY_CONFIG_TEST)
    def test_discovery_filtering_sex_none_in_project_full(self):
        response = self.dt_authz_full_get(f"/api/discovery?project={self.project_2.identifier}&sex=female")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # TODO: assert full empty response
        # TODO: full empty fields assertion
        self.assertDictEqual(response.json()["counts"], DISCOVERY_ZERO_COUNTS)

    @override_settings(CONFIG_PUBLIC=DISCOVERY_CONFIG_TEST)
    def test_discovery_filtering_sex_none_in_project_dataset_full(self):
        response = self.dt_authz_full_get(
            f"/api/discovery?project={self.project_2.identifier}&dataset={self.dataset_2.identifier}&sex=female"
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # TODO: full empty fields assertion
        # TODO: assert full empty response
        self.assertDictEqual(response.json()["counts"], DISCOVERY_ZERO_COUNTS)

    def _test_individual_counts(self, response_obj: dict, individual_db_count: int):
        if individual_db_count <= self.response_threshold:
            self.assertEqual(response_obj["counts"], DISCOVERY_ZERO_COUNTS)
            self.assertEqual(response_obj["message"], dres.INSUFFICIENT_DATA_AVAILABLE_MSG)
        else:
            self.assertEqual(individual_db_count, response_obj["counts"]["individual"])

    @override_settings(CONFIG_PUBLIC=DISCOVERY_CONFIG_EXTRA_PROPERTIES)
    def test_discovery_filtering_sex_via_fts(self):
        # sex string search using full-text search as a proxy for the unique keyword we have in the sex field:
        response = self.dt_authz_counts_get('/api/discovery?_fts=FEMALE')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        response_obj = response.json()
        db_count = Individual.objects.filter(sex__iexact='female').count()
        self.assertIn(self.response_threshold_check(response_obj), [db_count, dres.INSUFFICIENT_DATA_AVAILABLE])
        self._test_individual_counts(response_obj, db_count)

    @override_settings(CONFIG_PUBLIC=DISCOVERY_CONFIG_EXTRA_PROPERTIES)
    def test_discovery_filtering_sex_via_fts_trigram(self):
        # sex string search using full-text search as a proxy for the unique keyword we have in the sex field
        # with trigram search, our strict similarity for smaller queries means this will return only males despite
        # 'female' containing 'male'.

        params = [
            ("female", Q(sex="UNKNOWN_SEX")),
            ("male", Q(sex="MALE")),
            ("unkn_sex", Q(sex="UNKNOWN_SEX")),
            ("unknw_sex", Q(sex="UNKNOWN_SEX")),
            # word search means this 'unknown' matches other stuff too:
            ("unknown_sex", Q(sex="UNKNOWN_SEX")),
            ("unknown", Q(sex="UNKNOWN_SEX") | Q(karyotypic_sex="UNKNOWN_KARYOTYPE")),
            ("unknown_", Q(sex="UNKNOWN_SEX") | Q(karyotypic_sex="UNKNOWN_KARYOTYPE")),
            ("other", Q(sex="OTHER_SEX")),
            ("oth", Q(sex="OTHER_SEX")),
        ]
        for p in params:
            with self.subTest(params=p):
                response = self.dt_authz_counts_get(f"/api/discovery?_fts={p[0].upper()}&_fts_type=trigram")
                self.assertEqual(response.status_code, status.HTTP_200_OK)
                response_obj = response.json()
                db_count = Individual.objects.filter(p[1]).count()
                self.assertIn(
                    self.response_threshold_check(response_obj),
                    [db_count, dres.INSUFFICIENT_DATA_AVAILABLE],
                )
                self._test_individual_counts(response_obj, db_count)

    @override_settings(CONFIG_PUBLIC=DISCOVERY_CONFIG_EXTRA_PROPERTIES)
    def test_discovery_filtering_2_fields(self):
        # sex and extra_properties string search
        # test GET query string search for extra_properties field
        response = self.dt_authz_counts_get('/api/discovery?sex=female&smoking=Smoker')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        response_obj = response.json()
        db_count = Individual.objects.filter(
            sex__iexact='female', extra_properties__contains={"smoking": "Smoker"}
        ).count()
        self.assertIn(self.response_threshold_check(response_obj), [db_count, dres.INSUFFICIENT_DATA_AVAILABLE])
        self._test_individual_counts(response_obj, db_count)

    # test the same as above but with an empty CONFIG_PUBLIC
    @override_settings(CONFIG_PUBLIC=DiscoveryConfig())
    def test_discovery_filtering_2_fields_config_empty(self):
        # sex and extra_properties string search
        # test GET query string search for extra_properties field
        response = self.dt_authz_counts_get('/api/discovery?sex=female&smoking=Non-smoker')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        response_obj = response.json()
        self.assertIsInstance(response_obj, dict)
        self.assertEqual(response_obj, dres.NO_PUBLIC_DATA_AVAILABLE)

    @override_settings(CONFIG_PUBLIC=DISCOVERY_CONFIG_EXTRA_PROPERTIES)
    def test_discovery_filtering_extra_properties_1(self):
        # extra_properties string search (multiple values)
        response = self.dt_authz_counts_get('/api/discovery?smoking=Non-smoker&death_dc=Deceased')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        response_obj = response.json()
        db_count = Individual.objects.filter(
            extra_properties__contains={"smoking": "Non-smoker", "death_dc": "Deceased"}
        ).count()
        self.assertIn(self.response_threshold_check(response_obj), [db_count, dres.INSUFFICIENT_DATA_AVAILABLE])
        self._test_individual_counts(response_obj, db_count)

    # test the same as above but with an empty CONFIG_PUBLIC
    @override_settings(CONFIG_PUBLIC=DiscoveryConfig())
    def test_discovery_filtering_extra_properties_1_config_empty(self):
        # extra_properties string search
        # test GET query string search for extra_properties field
        response = self.dt_authz_counts_get('/api/discovery?smoking=Non-smoker&death_dc=Deceased')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        response_obj = response.json()
        self.assertIsInstance(response_obj, dict)
        self.assertEqual(response_obj, dres.NO_PUBLIC_DATA_AVAILABLE)

    @override_settings(CONFIG_PUBLIC=DISCOVERY_CONFIG_EXTRA_PROPERTIES)
    def test_discovery_filtering_extra_properties_2(self):
        # extra_properties string search (multiple values)
        response = self.dt_authz_counts_get(
            '/api/discovery?smoking=Non-smoker&death_dc=deceased&covidstatus=positive'
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        response_obj = response.json()
        self.assertEqual(response_obj["code"], status.HTTP_400_BAD_REQUEST)

    @override_settings(CONFIG_PUBLIC=DISCOVERY_CONFIG_EXTRA_PROPERTIES)
    def test_discovery_filtering_extra_properties_invalid_3(self):
        # if GET query string list has various data types Error
        response = self.dt_authz_counts_get('/api/discovery?extra_properties=[{"smoking": "Non-smoker"}, 5, "Test"]')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        response_obj = response.json()
        self.assertEqual(response_obj["code"], status.HTTP_400_BAD_REQUEST)

    @override_settings(CONFIG_PUBLIC=DISCOVERY_CONFIG_EXTRA_PROPERTIES)
    def test_discovery_filtering_extra_properties_range_1(self):
        # extra_properties range search (both min and max ranges, single value)
        response = self.dt_authz_counts_get(
            '/api/discovery?lab_test_result_value=[200, 300)'
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        response_obj = response.json()
        range_parameters = {
            "extra_properties__lab_test_result_value__gte": 200,
            "extra_properties__lab_test_result_value__lt": 300
        }
        db_count = Individual.objects.filter(**range_parameters).count()
        self.assertIn(self.response_threshold_check(response_obj), [db_count, dres.INSUFFICIENT_DATA_AVAILABLE])
        self._test_individual_counts(response_obj, db_count)

    @override_settings(CONFIG_PUBLIC=DISCOVERY_CONFIG_EXTRA_PROPERTIES)
    def test_discovery_filtering_extra_properties_range_2(self):
        # extra_properties range search (above taper, single value)
        response = self.dt_authz_counts_get(
            '/api/discovery?baseline_creatinine=≥ 200'
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        response_obj = response.json()
        range_parameters = {
            "extra_properties__baseline_creatinine__gte": 200,
        }
        db_count = Individual.objects.filter(**range_parameters).count()
        self.assertIn(self.response_threshold_check(response_obj), [db_count, dres.INSUFFICIENT_DATA_AVAILABLE])
        self._test_individual_counts(response_obj, db_count)

    @override_settings(CONFIG_PUBLIC=DISCOVERY_CONFIG_EXTRA_PROPERTIES)
    def test_discovery_filtering_extra_properties_range_3(self):
        # extra_properties range search (below taper, single value)
        response = self.dt_authz_counts_get(
            '/api/discovery?baseline_creatinine=< 50'
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        response_obj = response.json()
        range_parameters = {
            "extra_properties__baseline_creatinine__lt": 50,
        }
        db_count = Individual.objects.filter(**range_parameters).count()
        self.assertIn(self.response_threshold_check(response_obj), [db_count, dres.INSUFFICIENT_DATA_AVAILABLE])
        self._test_individual_counts(response_obj, db_count)

    @override_settings(CONFIG_PUBLIC=DISCOVERY_CONFIG_EXTRA_PROPERTIES)
    def test_discovery_filtering_extra_properties_wrong_range(self):
        # extra_properties range search, unauthorized range
        response = self.dt_authz_counts_get(
            '/api/discovery?lab_test_result_value=[100, 200)'
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        response_obj = response.json()
        self.assertEqual(response_obj["code"], status.HTTP_400_BAD_REQUEST)

    @override_settings(CONFIG_PUBLIC=DISCOVERY_CONFIG_EXTRA_PROPERTIES)
    def test_discovery_filtering_extra_properties_bad_range_format(self):
        # extra_properties range search (above taper, single value)
        response = self.dt_authz_counts_get("/api/discovery?baseline_creatinine=+ 200")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    @override_settings(CONFIG_PUBLIC=DISCOVERY_CONFIG_EXTRA_PROPERTIES)
    def test_discovery_filtering_extra_properties_range_string_1(self):
        # test combined sex string search + extra_properties range search,
        # with variety of ranges for lab_test_result_value including some decimal ones (which used to not work!)

        subtests = [
            ("< 55.5", 0, 55.5),
            ("[200, 300)", 200, 300),
            ("[1000, 1255.5)", 1000, 1255.5),
            ("[1255.5, 1500)", 1000, 1255.5),
        ]

        for params in subtests:
            with self.subTest(params=params):
                # sex string search and extra_properties range search
                response = self.dt_authz_counts_get(f"/api/discovery?sex=female&lab_test_result_value={params[0]}")
                self.assertEqual(response.status_code, status.HTTP_200_OK)
                response_obj = response.json()
                range_parameters = {
                    "sex__iexact": "female",
                    "extra_properties__lab_test_result_value__gte": params[1],
                    "extra_properties__lab_test_result_value__lt": params[2],
                }
                db_count = Individual.objects.filter(**range_parameters).count()
                self.assertIn(self.response_threshold_check(response_obj), [db_count, dres.INSUFFICIENT_DATA_AVAILABLE])
                self._test_individual_counts(response_obj, db_count)

    @override_settings(CONFIG_PUBLIC=DISCOVERY_CONFIG_EXTRA_PROPERTIES)
    def test_discovery_filtering_extra_properties_range_string_2(self):
        # extra_properties range search and extra_properties string search (single value)

        response = self.dt_authz_counts_get(
            '/api/discovery?lab_test_result_value=< 55.5&covidstatus=positive'
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        response_obj = response.json()
        range_parameters = {
            "extra_properties__lab_test_result_value__gte": 0,
            "extra_properties__lab_test_result_value__lt": 55.5,
            "extra_properties__covidstatus__iexact": "positive",
        }

        db_count = Individual.objects.filter(**range_parameters).count()

        self.assertIn(self.response_threshold_check(response_obj), [db_count, dres.INSUFFICIENT_DATA_AVAILABLE])
        self._test_individual_counts(response_obj, db_count)

    @override_settings(CONFIG_PUBLIC=DISCOVERY_CONFIG_EXTRA_PROPERTIES)
    def test_discovery_filtering_extra_properties_multiple_ranges_1(self):
        # extra_properties range search (both min and max range, multiple values)
        response = self.dt_authz_counts_get(
            '/api/discovery?lab_test_result_value=< 55.5&baseline_creatinine=[100, 150)'
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        response_obj = response.json()
        range_parameters = {
            "extra_properties__lab_test_result_value__gte": 0,
            "extra_properties__lab_test_result_value__lt": 55.5,
            "extra_properties__baseline_creatinine__gte": 100,
            "extra_properties__baseline_creatinine__lt": 150,
        }
        db_count = Individual.objects.filter(**range_parameters).count()
        self.assertIn(self.response_threshold_check(response_obj), [db_count, dres.INSUFFICIENT_DATA_AVAILABLE])
        self._test_individual_counts(response_obj, db_count)

    @override_settings(CONFIG_PUBLIC=DISCOVERY_CONFIG_EXTRA_PROPERTIES)
    def test_discovery_filtering_extra_properties_date_range_1(self):
        # extra_properties date range search (only after or before, single value)
        # Testing with a date of consent from 1 year ago
        response = self.dt_authz_counts_get(
            '/api/discovery?date_of_consent=Mar 2021'
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        response_obj = response.json()
        range_parameters = {
            "extra_properties__date_of_consent__startswith": "2021-03"
        }
        db_count = Individual.objects.filter(**range_parameters).count()
        self.assertIn(self.response_threshold_check(response_obj), [db_count, dres.INSUFFICIENT_DATA_AVAILABLE])
        self._test_individual_counts(response_obj, db_count)

    @override_settings(CONFIG_PUBLIC=DISCOVERY_CONFIG_EXTRA_PROPERTIES)
    def test_discovery_filtering_extra_properties_date_range_and_other_range(self):
        # extra_properties date range search (both after and before, single value) and other number range search
        # Testing with a date of consent from 2 years ago
        response = self.dt_authz_counts_get(
            '/api/discovery?date_of_consent=Mar 2021&lab_test_result_value=< 55.5'
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        response_obj = response.json()
        range_parameters = {
            "extra_properties__date_of_consent__startswith": "2021-03",
            "extra_properties__lab_test_result_value__gte": 0,
            "extra_properties__lab_test_result_value__lt": 55.5,
        }
        db_count = Individual.objects.filter(**range_parameters).count()
        self.assertIn(self.response_threshold_check(response_obj), [db_count, dres.INSUFFICIENT_DATA_AVAILABLE])
        self._test_individual_counts(response_obj, db_count)

    @override_settings(CONFIG_PUBLIC=CONFIG_PUBLIC_TEST_NO_THRESHOLD)
    def test_discovery_filtering_mapping_for_search_filter(self):
        # biosample tissue field search
        response = self.dt_authz_counts_get('/api/discovery?tissues=wall of urinary bladder')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        response_obj = response.json()
        self.assertDictEqual(response_obj["counts"], {
            "phenopacket": 1,
            "individual": 1,
            "biosample": 1,  # biosample 2 does not match "wall of urinary bladder"
            "experiment": 2,  # both experiments are on biosample 1
            "experiment_result": 0,
        })

    @override_settings(CONFIG_PUBLIC=CONFIG_PUBLIC_TEST_NO_THRESHOLD)
    def test_discovery_filtering_two_experiments(self):
        response = self.dt_authz_counts_get(f"/api/discovery?sex={self.individuals[0]['sex']}&extraction_protocol=NGS")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        response_obj = response.json()
        self.assertDictEqual(response_obj["counts"], {
            "phenopacket": 1,
            "individual": 1,
            "biosample": 1,  # biosample 2 does not have any experiments
            "experiment": 2,
            "experiment_result": 0,
        })

    @override_settings(CONFIG_PUBLIC=DISCOVERY_CONFIG_TEST)
    def test_discovery_sex(self):
        response = self.dt_authz_counts_get(reverse("discovery-search-fields"))

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        response_obj = response.json()

        # overview for sex should have entries due to large cell counts: MALE, FEMALE, UNKNOWN, OTHER
        self.assertEqual(
            len(response_obj["sections"][0]["fields"][0]["options"]),
            # This inline if statement handles the below small cell count version of this test class!
            4 if self.num_individuals > DISCOVERY_CONFIG_TEST.rules.count_threshold else 0
        )  # path to sex field


class DiscoveryFilteringIndividualsTestSmallCellCount(DiscoveryFilteringIndividualsTest):
    num_individuals = 3  # below configured config.rules.count_threshold
    # rest of the methods are inherited


class RenderAgeTest(TestCase):
    def setUp(self):
        self.individual_three = c.VALID_INDIVIDUAL_3

    def test_render_age(self):
        result = render_age(self.individual_three, 'time_at_last_encounter')
        self.assertIsNone(result)

    def test_age_duration(self):
        subject_with_age = {
            **c.VALID_INDIVIDUAL_3,
            "time_at_last_encounter": {
                "age": {
                    "iso8601duration": "P50Y"
                }
            }
        }
        result = render_age(subject_with_age, 'time_at_last_encounter')
        self.assertEqual(result, "P50Y")

    def test_age_none(self):
        subject_with_age = {
            **c.VALID_INDIVIDUAL_3,
            "time_at_last_encounter": {}
        }
        result = render_age(subject_with_age, 'time_at_last_encounter')
        self.assertIsNone(result)


class DiscoveryAgeRangeFilteringIndividualsTest(AuthzAPITestCase):
    """ Test for api/public GET filtering """

    response_threshold = 5
    random_range = 45

    @staticmethod
    def response_threshold_check(response):
        return response['count'] if 'count' in response else dres.INSUFFICIENT_DATA_AVAILABLE

    def setUp(self):
        individuals = [
            c.generate_valid_individual(gen_random_age=(1, 100))
            for _ in range(self.random_range)
        ]
        for individual in individuals:
            Individual.objects.create(**individual)

        for individual in Individual.objects.all():
            if individual.time_at_last_encounter:
                if "age" in individual.time_at_last_encounter:
                    age_numeric, age_unit = iso_duration_to_years(individual.time_at_last_encounter["age"])
                    individual.age_numeric = age_numeric
                    individual.age_unit = age_unit if age_unit else ""
                    individual.save()

    @override_settings(CONFIG_PUBLIC=DISCOVERY_CONFIG_TEST)
    def test_discovery_filtering_age_range(self):
        # age valid range search
        response = self.dt_authz_counts_get('/api/discovery?age=[20, 30)')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        response_obj = response.json()
        db_count = Individual.objects.filter(age_numeric__gte=20, age_numeric__lt=30).count()
        self.assertIn(self.response_threshold_check(response_obj), [db_count, dres.INSUFFICIENT_DATA_AVAILABLE])
        if db_count <= self.response_threshold:
            self.assertEqual(response_obj["counts"], DISCOVERY_ZERO_COUNTS)
            self.assertEqual(response_obj["message"], dres.INSUFFICIENT_DATA_AVAILABLE_MSG)
        else:
            self.assertEqual(db_count, response_obj['count'])

    @override_settings(CONFIG_PUBLIC=DISCOVERY_CONFIG_TEST)
    def test_discovery_filtering_age_invalid_range(self):
        # age invalid range max search
        response = self.dt_authz_counts_get('/api/discovery?age=[10, 50)')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        response_obj = response.json()
        self.assertEqual(response_obj["code"], status.HTTP_400_BAD_REQUEST)

    @override_settings(CONFIG_PUBLIC=CONFIG_PUBLIC_TEST_SEARCH_SEX_ONLY)
    def test_discovery_filtering_age_range_min_and_max_no_age_in_config(self):
        # test with config without age field, returns error
        response = self.dt_authz_counts_get('/api/discovery?age=[20, 30)')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        response_obj = response.json()
        self.assertEqual(response_obj["code"], status.HTTP_400_BAD_REQUEST)

    @override_settings(CONFIG_PUBLIC=DiscoveryConfig())
    def test_discovery_filtering_age_range_min_and_max_no_config(self):
        # test when config is not provided, returns NO_PUBLIC_DATA_AVAILABLE
        response = self.dt_authz_counts_get('/api/discovery?age=[20, 30)')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        response_obj = response.json()
        self.assertIsInstance(response_obj, dict)
        self.assertEqual(response_obj, dres.NO_PUBLIC_DATA_AVAILABLE)


class DiscoveryFilteringMatchesTest(AuthzAPITestCase):

    random_range = 20

    def setUp(self):
        # equal number of each sex option instead of relying on RNG
        individuals = [c.generate_valid_individual(sex_idx=i % 4) for i in range(self.random_range)]

        for i, individual in enumerate(individuals):
            ind_obj = Individual.objects.create(**individual)
            md = ph_m.MetaData.objects.create(**ph_c.VALID_META_DATA_1)
            ph_m.Phenopacket.objects.create(id=f"phe={i}", subject=ind_obj, meta_data=md)

    def _assert_ok_page_length_and_total(self, response, results_length: int, total: int):
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        response_obj = response.json()
        self.assertEqual(len(response_obj["results"]), results_length)
        self.assertEqual(response_obj["pagination"]["total"], total)

    @override_settings(CONFIG_PUBLIC=DiscoveryConfig())
    def test_discovery_matches_response_no_discovery_config(self):
        response = self.dt_authz_full_get('/api/discovery_matches?sex=MALE')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(response.json()["message"], "No public data available.")

    @override_settings(CONFIG_PUBLIC=DISCOVERY_CONFIG_TEST)
    def test_discovery_matches_response_insufficient_perms(self):
        response = self.dt_authz_counts_get('/api/discovery_matches?sex=MALE')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(response.json()["message"], "Insufficient privileges to view data.")

    @override_settings(CONFIG_PUBLIC=DISCOVERY_CONFIG_TEST)
    def test_discovery_matches_response_invalid_entity(self):
        response = self.dt_authz_full_get('/api/discovery_matches?sex=MALE&_entity=does-not-exist')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.json()["message"], "Bad Request")

    @override_settings(CONFIG_PUBLIC=DISCOVERY_CONFIG_TEST)
    def test_discovery_matches_bad_scope(self):
        res = self.dt_authz_full_get("/api/discovery_matches?project=does-not-exist")
        self.assertEqual(res.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(res.json()["message"], "Not Found")

    @override_settings(CONFIG_PUBLIC=DISCOVERY_CONFIG_TEST)
    def test_discovery_matches_response(self):
        # We have phenopackets for each individual, so the count should be the same as the # of individuals
        response = self.dt_authz_full_get('/api/discovery_matches?sex=MALE')
        male_count = Individual.objects.filter(sex="MALE").count()  # proxy for phenopackets since we have 1:1
        # male_count=5 males, all of which can fit in the default page size of 10:
        self._assert_ok_page_length_and_total(response, male_count, male_count)

    @override_settings(CONFIG_PUBLIC=DISCOVERY_CONFIG_TEST)
    def test_discovery_matches_response_individuals(self):
        response = self.dt_authz_full_get('/api/discovery_matches?sex=MALE&_entity=individual')
        male_count = Individual.objects.filter(sex="MALE").count()
        # male_count=5 males, all of which can fit in the default page size of 10:
        self._assert_ok_page_length_and_total(response, male_count, male_count)

    @override_settings(CONFIG_PUBLIC=DISCOVERY_CONFIG_TEST)
    def test_discovery_matches_response_empty_entities(self):
        # no biosamples, experiments, or experiment results in this test right now
        for entity in ("biosample", "experiment", "experiment_result"):
            with self.subTest(params=(entity,)):
                response = self.dt_authz_full_get(f"/api/discovery_matches?sex=MALE&_entity={entity}")
                self._assert_ok_page_length_and_total(response, 0, 0)

    @override_settings(CONFIG_PUBLIC=DISCOVERY_CONFIG_TEST)
    def test_discovery_matches_response_page_size(self):
        response = self.dt_authz_full_get('/api/discovery_matches?sex=MALE&_page_size=1')
        male_count = Individual.objects.filter(sex="MALE").count()
        # _page_size is 1, so we get 1 result with male_count=5 total records available:
        self._assert_ok_page_length_and_total(response, 1, male_count)

    @override_settings(CONFIG_PUBLIC=DISCOVERY_CONFIG_TEST)
    def test_discovery_matches_response_unlimited_page_size(self):
        response = self.dt_authz_full_get('/api/discovery_matches?_page_size=0')
        all_count = Individual.objects.count()
        # _page_size=0 means we get all records:
        self._assert_ok_page_length_and_total(response, all_count, all_count)

    @override_settings(CONFIG_PUBLIC=DISCOVERY_CONFIG_TEST)
    def test_discovery_matches_response_page_invalid_too_small(self):
        response = self.dt_authz_full_get('/api/discovery_matches?sex=MALE&page=-1')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)  # page number cannot be negative

    @override_settings(CONFIG_PUBLIC=DISCOVERY_CONFIG_TEST)
    def test_discovery_matches_response_page_invalid_too_big(self):
        response = self.dt_authz_full_get('/api/discovery_matches?sex=MALE&page_size=100&page=2')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)  # page number too high

    @override_settings(CONFIG_PUBLIC=DISCOVERY_CONFIG_TEST)
    def test_discovery_matches_response_page_invalid_string(self):
        response = self.dt_authz_full_get('/api/discovery_matches?sex=MALE&page=one')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)  # page number cannot be a string

    # TODO: more

    @override_settings(CONFIG_PUBLIC=DiscoveryConfig())
    def test_discovery_matches_response_no_config(self):
        # test when config is not provided, returns NOT FOUND
        response = self.dt_authz_full_get('/api/discovery_matches?sex=MALE')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    @override_settings(CONFIG_PUBLIC=DISCOVERY_CONFIG_TEST)
    def test_discovery_matches_response_invalid_search_key(self):
        response = self.dt_authz_full_get('/api/discovery_matches?birdwatcher=yes')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    @override_settings(CONFIG_PUBLIC=DISCOVERY_CONFIG_EXTRA_PROPERTIES)
    def test_discovery_matches_response_invalid_search_value(self):
        response = self.dt_authz_full_get('/api/discovery_matches?smoking=on_Sundays')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    @override_settings(CONFIG_PUBLIC=DISCOVERY_CONFIG_EXTRA_PROPERTIES)
    def test_discovery_matches_more_params_than_censorship_limit(self):
        response = self.dt_authz_full_get('/api/discovery_matches?sex=MALE&smoking=Non-smoker&death_dc=Deceased')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
