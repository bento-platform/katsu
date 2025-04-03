from http import HTTPStatus

import chord_metadata_service.mohpackets.permissible_values as PERM_VAL
from chord_metadata_service.mohpackets.models import Donor, PrimaryDiagnosis, Treatment
from chord_metadata_service.mohpackets.tests.endpoints.base import BaseTestCase
from chord_metadata_service.mohpackets.tests.factories import (
    DonorFactory,
    PrimaryDiagnosisFactory,
    TreatmentFactory,
)
from django.conf import settings

"""
    This module contains API tests related to overview endpoints.

    It includes tests for:
    - Displaying actual number if data >5
    - Censoring if data <5

    Author: Son Chau
"""


class OverviewTestCase(BaseTestCase):
    def setUp(self):
        super().setUp()
        self.patients_per_program_url = "/v3/discovery/overview/patients_per_program/"
        self.individual_count_url = "/v3/discovery/overview/individual_count/"
        self.gender_count_url = "/v3/discovery/overview/gender_count/"
        self.primary_site_count_url = "/v3/discovery/overview/primary_site_count/"
        self.treatment_type_count_url = "/v3/discovery/overview/treatment_type_count/"
        self.diagnosis_age_count_url = "/v3/discovery/overview/diagnosis_age_count/"
        # The default dataset contains fewer than 5 entries.
        # To test the censor requirement, we need to add:
        # - 5 more donors
        # - 5 more primary diagnoses
        # - 5 more treatments
        # This will help the dataset displays more than 5 entries.
        self.gender_man = PERM_VAL.GENDER[0]  # Man
        self.primary_site_sinus = PERM_VAL.PRIMARY_SITE[0]  # Accessory sinuses
        self.treatment_type_bone = PERM_VAL.TREATMENT_TYPE[0]  # Bone marrow transplant
        self.donors.extend(
            DonorFactory.create_batch(
                5,
                program_id=self.programs[0],
                gender=self.gender_man,
                date_of_birth={"day_interval": 27394},  # 70-79 age
            )
        )
        self.primary_diagnoses.extend(
            PrimaryDiagnosisFactory.create_batch(
                5,
                donor_uuid=self.donors[0],
                primary_site=self.primary_site_sinus,
            )
        )
        self.treatments.extend(
            TreatmentFactory.create_batch(
                5,
                primary_diagnosis_uuid=self.primary_diagnoses[0],
                treatment_type=[self.treatment_type_bone],
            )
        )

    def test_individual_count_api_no_censoring(self):
        """
        Verify individual_count endpoint does not censor number >5.

        Testing Strategy:
        - Total number of donors is 9
        - Send a request to individual_count endpoint
        - Ensure that the response show the full number
        """
        response = self.client.get(
            self.individual_count_url,
            HTTP_X_SERVICE_TOKEN=settings.QUERY_SERVICE_TOKEN,
        )
        self.assertEqual(response.status_code, HTTPStatus.OK)
        individual_count_value = response.json()["individual_count"]
        self.assertGreaterEqual(len(self.donors), 5)
        self.assertEqual(individual_count_value, str(len(self.donors)))

    def test_individual_count_api_censoring(self):
        """
        Verify individual_count endpoint censoring for small datasets.

        Testing Strategy:
        - Remove some donors (total count is 2 now)
        - Send a request to individual_count endpoint.
        - Ensure that the response does not reveal the number when it is less than 5.
        """
        Donor.objects.filter(program_id=self.programs[0]).delete()
        donors = Donor.objects.all()
        response = self.client.get(
            self.individual_count_url,
            HTTP_X_SERVICE_TOKEN=settings.QUERY_SERVICE_TOKEN,
        )
        self.assertEqual(response.status_code, HTTPStatus.OK)
        individual_count_value = response.json()["individual_count"]
        self.assertLess(len(donors), 5)
        self.assertEqual(individual_count_value, "<5")

    def test_patients_per_program_api_censoring(self):
        """
        Verify the censoring of patient counts per program endpoint.

        Testing Strategy:
        - Program 0 has 7, Program 1 has 2 donors
        - Send a request to patients_per_program endpoint.
        - Ensure that the response does not reveal the number when it is less than 5 donors.
        """
        response = self.client.get(
            self.patients_per_program_url,
            HTTP_X_SERVICE_TOKEN=settings.QUERY_SERVICE_TOKEN,
        )
        self.assertEqual(response.status_code, HTTPStatus.OK)
        for item in response.json():
            patients_count_value = item["patients_count"]
            patients_count = Donor.objects.filter(program_id=item["program_id"]).count()
            if patients_count < 5:
                self.assertEqual(patients_count_value, "<5")
            else:
                self.assertEqual(patients_count_value, str(patients_count))

    def test_gender_count_api_censoring(self):
        """
        Test gender count API censoring for small datasets.

        Testing Strategy:
        - "Man" gender is greater or equal to 5
        - Other genders is less than 5
        - Send a request to gender_count endpoint.
        - Ensure that the response does not reveal the count when it is less than 5.
        """

        response = self.client.get(
            self.gender_count_url,
            HTTP_X_SERVICE_TOKEN=settings.QUERY_SERVICE_TOKEN,
        )
        self.assertEqual(response.status_code, HTTPStatus.OK)
        for item in response.json():
            gender_count_value = item["gender_count"]
            gender_count = Donor.objects.filter(gender=item["gender"]).count()
            if gender_count < 5:
                self.assertEqual(gender_count_value, "<5")
            else:
                self.assertEqual(gender_count_value, str(gender_count))

    def test_primary_site_count_api_censoring(self):
        """
        Test primary site count API censoring for small datasets.

        Testing Strategy:
        - "Accessory sinuses" primary site is greater or equal to 5
        - Other primary site is less than 5
        - Send a request to primary_site_count endpoint.
        - Ensure that the response does not reveal the count when it is less than 5.
        """
        response = self.client.get(
            self.primary_site_count_url,
            HTTP_X_SERVICE_TOKEN=settings.QUERY_SERVICE_TOKEN,
        )
        self.assertEqual(response.status_code, HTTPStatus.OK)
        for item in response.json():
            primary_site_count_value = item["primary_site_count"]
            primary_site_count = PrimaryDiagnosis.objects.filter(
                primary_site=item["primary_site_name"]
            ).count()
            if primary_site_count < 5:
                self.assertEqual(primary_site_count_value, "<5")
            else:
                self.assertEqual(primary_site_count_value, str(primary_site_count))

    def test_treatment_type_count_api_censoring(self):
        """
        Test treatment type count count API censoring for small datasets.

        Testing Strategy:
        - "Bone marrow transplant" treatment type is greater or equal to 5
        - Other treatment type should be less than 5 (but might not since randomized)
        - Send a request to treatment_type_count endpoint.
        - Ensure that the response does not reveal the count when it is less than 5.
        """
        response = self.client.get(
            self.treatment_type_count_url,
            HTTP_X_SERVICE_TOKEN=settings.QUERY_SERVICE_TOKEN,
        )
        self.assertEqual(response.status_code, HTTPStatus.OK)
        for item in response.json():
            treatment_type_count_value = item["treatment_type_count"]
            treatment_type_count = Treatment.objects.filter(
                treatment_type__contains=[item["treatment_type_name"]]
            ).count()
            if treatment_type_count < 5:
                self.assertEqual(treatment_type_count_value, "<5")
            else:
                self.assertEqual(treatment_type_count_value, str(treatment_type_count))

    def test_diagnosis_age_count_api_censoring(self):
        """
        Test diagnosis age count count API censoring for small datasets.

        Testing Strategy:
        - "70-79" age bracket is greater or equal to 5
        - Other age bracket is less than 5
        - Send a request to diagnosis_age_count endpoint.
        - Ensure that the response does not reveal the count when it is less than 5.
        """
        response = self.client.get(
            self.diagnosis_age_count_url,
            HTTP_X_SERVICE_TOKEN=settings.QUERY_SERVICE_TOKEN,
        )
        self.assertEqual(response.status_code, HTTPStatus.OK)
        for item in response.json():
            if item["age_at_diagnosis"] != "70-79":
                self.assertEqual(item["age_count"], "<5")
