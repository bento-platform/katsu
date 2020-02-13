from django.test import TestCase
from chord_metadata_service.patients.tests.es_mocks import es  # noqa: F401
from ..models import Individual


class IndividualTest(TestCase):
    """ Test module for Individual model """

    def setUp(self):
        Individual.objects.create(id='patient:1', sex='FEMALE', age={"age": "P25Y3M2D"})
        Individual.objects.create(id='patient:2', sex='FEMALE', age={"age": "P45Y3M2D"})

    def test_individual(self):
        individual_one = Individual.objects.get(id='patient:1')
        individual_two = Individual.objects.get(id='patient:2')
        self.assertEqual(individual_one.sex, 'FEMALE')
        self.assertEqual(individual_two.age, {"age": "P45Y3M2D"})
