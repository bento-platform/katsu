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


class ExperimentTest(TestCase):
    """ Test module for Experiment model """

    def setUp(self):
        i = Individual.objects.create(**VALID_INDIVIDUAL_1)
        p = Procedure.objects.create(**VALID_PROCEDURE_1)
        self.biosample = Biosample.objects.create(**valid_biosample_1(i, p))
        Experiment.objects.create(
            id="experiment:1",
            study_type="Whole genome Sequencing",
            experiment_type="Chromatin Accessibility",
            experiment_ontology=[{"id": "ontology:1", "label": "Ontology term 1"}],
            molecule="total RNA",
            molecule_ontology=[{"id": "ontology:1", "label": "Ontology term 1"}],
            library_strategy="Bisulfite-Seq",
            library_source="Genomic",
            library_selection="PCR",
            library_layout="Single",
            extraction_protocol="NGS",
            reference_registry_id="some_id",
            qc_flags=["flag 1", "flag 2"],
            extra_properties={"some_field": "value"},
            biosample=self.biosample
        )

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

        # Invalid molecule_ontology
        self.assertRaises(
            serializers.ValidationError,
            self.create,
            library_strategy="Bisulfite-Seq",
            experiment_type="Chromatin Accessibility",
            molecule_ontology=[{"id": "some_id"}],
            biosample=self.biosample
        )

        # Invalid value in other_fields
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
        ExperimentResult.objects.create(
            identifier="experiment_result:1",
            description="Test Experiment result 1",
            filename="01.vcf.gz",
            file_format="VCF",
            data_output_type="Derived data",
            usage="download",
            creation_date="2021-06-28",
            created_by="admin",
            extra_properties={"target": "None"}
        )

    @staticmethod
    def create(**kwargs):
        e = ExperimentResult(**kwargs)
        e.full_clean()
        e.save()

    def test_validation(self):
        self.assertEqual(ExperimentResult.objects.count(), 1)
        # Invalid CV for data_output_type
        # exceptions.ValidationError: {'data_output_type': ["Value 'Derived' is not a valid choice."]}
        self.assertRaises(
            ValidationError,
            self.create,
            identifier="experiment_result:2",
            description="Test Experiment result 2",
            filename="01.vcf.gz",
            file_format="VCF",
            data_output_type="Derived",
            usage="visualized",
            creation_date="2021-05-10",
            created_by="admin",
            extra_properties={"target": "None"}
        )

        # Invalid CV for data_output_type
        # exceptions.ValidationError: {'file_format': ["Value 'Not VCF' is not a valid choice."]}
        self.assertRaises(
            ValidationError,
            self.create,
            identifier="experiment_result:2",
            description="Test Experiment result 2",
            filename="01.vcf.gz",
            file_format="Not VCF",
            data_output_type="Derived data",
            usage="visualized",
            creation_date="2021-05-10",
            created_by="admin",
            extra_properties={"target": "None"}
        )


class InstrumentTest(TestCase):
    """ Test module for ExperimentResult model """

    def setUp(self):
        Instrument.objects.create(
            identifier="instrument:01",
            platform="Illumina",
            description="Test description 1",
            model="Illumina HiSeq 4000",
            extra_properties={"date": "2021-06-21"}
        )

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
