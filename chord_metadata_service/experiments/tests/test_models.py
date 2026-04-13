from django.test import TestCase
from django.core.exceptions import ValidationError
from rest_framework import serializers

from ..models import Experiment, ExperimentResult, Instrument
from .constants import valid_experiment_result, valid_instrument
from .helpers import ExperimentTestCase


class ExperimentTest(ExperimentTestCase):
    """ Test module for Experiment model """

    @staticmethod
    def create(**kwargs):
        e = Experiment(id="experiment:2", **kwargs)
        e.full_clean()
        e.save()

    def test_fts_extra(self):
        self.assertEqual(self.experiment.fts_extra, "")

    def test_str_rep(self):
        self.assertEqual(str(self.experiment), self.experiment.id)

    def test_validation(self):
        # Invalid experiment_ontology
        self.assertRaises(
            serializers.ValidationError,
            self.create,
            library_strategy="Bisulfite-Seq",
            experiment_type="DNA Methylation Array",
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
            experiment_type="DNA Methylation Array",
            molecule_ontology=[{"id": "some_id"}],
            biosample=self.biosample
        )

        # valid value in extra_properties
        try:
            self.create(
                library_strategy="Bisulfite-Seq",
                experiment_type="DNA Methylation Array",
                extra_properties={"some_field": "value", "invalid_value": 42},
                biosample=self.biosample
            )
        except Exception as e:
            self.fail(f"ExperimentResult creation with arbitrary extra_properties should succeed, got: {e}")

        # Missing biosample
        self.assertRaises(
            ValidationError,
            self.create,
            library_strategy="Bisulfite-Seq",
            experiment_type="DNA Methylation Array"
        )


class ExperimentResultTest(TestCase):
    """ Test module for ExperimentResult model """

    def setUp(self):
        self.exp_res = ExperimentResult.objects.create(**valid_experiment_result())

    @staticmethod
    def create(**kwargs):
        e = ExperimentResult(**kwargs)
        e.full_clean()
        e.save()

    # TODO: Fix the mess
    # def test_str_rep(self):
    #     self.assertEqual(str(self.exp_res), self.exp_res.id)

    def test_validation(self):
        self.assertEqual(ExperimentResult.objects.count(), 1)
        self.assertEqual(ExperimentResult.objects.filter(file_format="VCF").count(), 1)
        # Valid extra_properties

        try:
            self.create(
                identifier="experiment_results:1",
                description="Test description",
                filename="test.vcf",
                extra_properties={"date": 2021}
            )
        except Exception as e:
            self.fail(f"ExperimentResult creation with arbitrary extra_properties should succeed, got: {e}")

        obj = ExperimentResult.objects.get(identifier="experiment_results:1")
        self.assertEqual(obj.extra_properties.get("date"), 2021)


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
        # Valid CV for extra_properties
        try:
            self.create(
                device="Illumina HiScanSQ",
                description="Test description 2",
                extra_properties={"date": 2021}
            )
        except Exception as e:
            self.fail(f"Instrument creation with arbitrary extra_properties should succeed, got: {e}")
        obj = Instrument.objects.get(device="Illumina HiScanSQ")
        self.assertEqual(obj.extra_properties.get("date"), 2021)
