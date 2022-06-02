from django.test import TestCase
from django.core.exceptions import ValidationError
from rest_framework import serializers
from chord_metadata_service.patients.models import Individual
from chord_metadata_service.phenopackets.models import Biosample, Procedure
from ..models import Experiment, ExperimentResult, Instrument
from chord_metadata_service.phenopackets.tests.constants import (
    VALID_PROCEDURE_1,
    VALID_INDIVIDUAL_1,
    valid_biosample_1
)
from .constants import valid_experiment, valid_experiment_result, valid_instrument


class ExperimentTest(TestCase):
    """ Test module for Experiment model """

    def setUp(self):
        i = Individual.objects.create(**VALID_INDIVIDUAL_1)
        p = Procedure.objects.create(**VALID_PROCEDURE_1)
        self.biosample = Biosample.objects.create(**valid_biosample_1(i, p))
        Experiment.objects.create(**valid_experiment(self.biosample))

    @staticmethod
    def create(**kwargs):
        e = Experiment(id="experiment:2", **kwargs)
        e.full_clean()
        e.save()

    def test_validation(self):
        # Invalid experiment_ontology
        self.assertRaises(
            serializers.ValidationError,
            self.create,
            library_strategy="Bisulfite-Seq",
            experiment_type="Chromatin Accessibility",
            experiment_ontology=["invalid_value"],
            biosample=self.biosample
        )
        # Missing required experiment_type
        self.assertRaises(
            ValidationError,
            self.create,
            library_strategy="Bisulfite-Seq",
            biosample=self.biosample
        )

        # Invalid molecule_ontology
        self.assertRaises(
            serializers.ValidationError,
            self.create,
            library_strategy="Bisulfite-Seq",
            experiment_type="Chromatin Accessibility",
            molecule_ontology=[{"id": "some_id"}],
            biosample=self.biosample
        )

        # Invalid value in extra_properties
        self.assertRaises(
            serializers.ValidationError,
            self.create,
            library_strategy="Bisulfite-Seq",
            experiment_type="Chromatin Accessibility",
            extra_properties={"some_field": "value", "invalid_value": 42},
            biosample=self.biosample
        )

        # Missing biosample
        self.assertRaises(
            ValidationError,
            self.create,
            library_strategy="Bisulfite-Seq",
            experiment_type="Chromatin Accessibility"
        )


class ExperimentResultTest(TestCase):
    """ Test module for ExperimentResult model """

    def setUp(self):
        ExperimentResult.objects.create(**valid_experiment_result())

    @staticmethod
    def create(**kwargs):
        e = ExperimentResult(**kwargs)
        e.full_clean()
        e.save()

    def test_validation(self):
        self.assertEqual(ExperimentResult.objects.count(), 1)
        self.assertEqual(ExperimentResult.objects.filter(file_format="VCF").count(), 1)
        # Invalid extra_properties
        # serializers.ValidationError("Not valid JSON schema for this field.")
        self.assertRaises(
            serializers.ValidationError,
            self.create,
            identifier="experiment_results:1",
            description="Test description",
            filename="test.vcf",
            extra_properties={"date": 2021}
        )


class InstrumentTest(TestCase):
    """ Test module for ExperimentResult model """

    def setUp(self):
        Instrument.objects.create(**valid_instrument())

    @staticmethod
    def create(**kwargs):
        e = Instrument(**kwargs)
        e.full_clean()
        e.save()

    def test_validation(self):
        self.assertEqual(Instrument.objects.count(), 1)
        # Invalid CV for extra_properties
        # serializers.ValidationError("Not valid JSON schema for this field.")
        self.assertRaises(
            serializers.ValidationError,
            self.create,
            platform="Illumina",
            description="Test description 2",
            model="Illumina HiScanSQ",
            extra_properties={"date": 2021}
        )
