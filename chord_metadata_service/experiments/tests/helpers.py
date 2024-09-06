from django.test import TestCase
from chord_metadata_service.patients.models import Individual
from chord_metadata_service.phenopackets.models import Biosample
from ..models import Experiment
from chord_metadata_service.phenopackets.tests.constants import (
    VALID_INDIVIDUAL_1,
    valid_biosample_1
)
from .constants import valid_experiment

__all__ = ["ExperimentTestCase"]


class ExperimentTestCase(TestCase):
    """ Test module for Experiment model """

    def setUp(self):
        i = Individual.objects.create(**VALID_INDIVIDUAL_1)
        self.biosample = Biosample.objects.create(**valid_biosample_1(i))
        self.experiment = Experiment.objects.create(**valid_experiment(self.biosample))
