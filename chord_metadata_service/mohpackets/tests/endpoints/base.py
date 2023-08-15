import logging
import os

import factory
from django.conf import settings
from django.test import TestCase
from rest_framework.test import APIClient

from chord_metadata_service.mohpackets.api_authorized import AuthorizedMixin
from chord_metadata_service.mohpackets.authentication import LocalAuthentication
from chord_metadata_service.mohpackets.tests.endpoints.factories import (
    ChemotherapyFactory,
    DonorFactory,
    PrimaryDiagnosisFactory,
    ProgramFactory,
    SampleRegistrationFactory,
    SpecimenFactory,
    TreatmentFactory,
)

"""
    This file contains the base test case class for testing endpoints.

    It sets up initial test data, including programs, donors with other models,
    and defines test users with different permission levels and dataset access.
    By utilizing this, there is no need to create the same test data
    for every individual test method, thereby speeding up the tests and promoting
    consistency.

    Example:
        To use this base test case, inherit from it in your test classes and use
        the provided attributes for testing API endpoints and permissions.

        class MyAPITestCase(BaseTestCase):
            def test_my_endpoint(self):
                # Write your test logic here using the initialized data and test users.
"""


class TestUser:
    def __init__(self, token, is_admin, datasets):
        self.token = token
        self.is_admin = is_admin
        self.datasets = datasets


class BaseTestCase(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.programs = ProgramFactory.create_batch(
            2,
        )
        cls.donors = DonorFactory.create_batch(
            4, program_id=factory.Iterator(cls.programs)
        )
        cls.primary_diagnoses = PrimaryDiagnosisFactory.create_batch(
            8, submitter_donor_id=factory.Iterator(cls.donors)
        )
        cls.specimens = SpecimenFactory.create_batch(
            16, submitter_primary_diagnosis_id=factory.Iterator(cls.primary_diagnoses)
        )
        cls.sample_registrations = SampleRegistrationFactory.create_batch(
            32, submitter_specimen_id=factory.Iterator(cls.specimens)
        )
        cls.treatments = TreatmentFactory.create_batch(
            16, submitter_primary_diagnosis_id=factory.Iterator(cls.primary_diagnoses)
        )
        cls.chemotherapies = ChemotherapyFactory.create_batch(
            4, submitter_treatment_id=factory.Iterator(cls.treatments)
        )

        # Define test users with permission and datasets access
        cls.user_0 = TestUser(
            token="token_0",
            is_admin=False,
            datasets=[],
        )
        cls.user_1 = TestUser(
            token="token_1",
            is_admin=False,
            datasets=[cls.programs[0].program_id],
        )
        cls.user_2 = TestUser(
            token="token_2",
            is_admin=True,
            datasets=[cls.programs[0].program_id, cls.programs[1].program_id],
        )
        # remember to add all the custom users into this list
        cls.users = [cls.user_0, cls.user_1, cls.user_2]
        os.environ["DJANGO_SETTINGS_MODULE"] = "config.settings.local"

        settings.LOCAL_AUTHORIZED_DATASET = [
            {
                "token": cls.user_0.token,
                "is_admin": cls.user_0.is_admin,
                "datasets": cls.user_0.datasets,
            },
            {
                "token": cls.user_1.token,
                "is_admin": cls.user_1.is_admin,
                "datasets": cls.user_1.datasets,
            },
            {
                "token": cls.user_2.token,
                "is_admin": cls.user_2.is_admin,
                "datasets": cls.user_2.datasets,
            },
        ]

    def setUp(self):
        logging.disable(logging.WARNING)
        # Initialize the client before each test method
        self.client = APIClient()
        AuthorizedMixin.authentication_classes = [LocalAuthentication]
