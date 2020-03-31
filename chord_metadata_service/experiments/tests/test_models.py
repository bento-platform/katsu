from django.test import TestCase
from django.core.exceptions import ValidationError
from rest_framework import serializers
from chord_metadata_service.patients.models import Individual
from ..models import Experiment


class ExperimentTest(TestCase):
    """ Test module for Experiment model """

    def setUp(self):
        Individual.objects.create(id='patient:1', sex='FEMALE', age={"age": "P25Y3M2D"})
        Experiment.objects.create(
            id='experiment:1',
            reference_registry_id='some_id',
            qc_flags=['flag 1', 'flag 2'],
            experiment_type='Chromatin Accessibility',
            experiment_ontology=[{"id": "ontology:1", "label": "Ontology term 1"}],
            molecule_ontology=[{"id": "ontology:1", "label": "Ontology term 1"}],
            molecule='total RNA',
            library_strategy='Bisulfite-Seq',
            other_fields={"some_field": "value"}
        )

    def create(self, **kwargs):
        e = Experiment(**kwargs)
        e.full_clean()
        e.save()

    def test_validation(self):
        individual_one = Individual.objects.get(id='patient:1')

        # Invalid experiment_ontology
        self.assertRaises(serializers.ValidationError, self.create,
                id='experiment:2',
                library_strategy='Bisulfite-Seq',
                experiment_type='Chromatin Accessibility',
                experiment_ontology=["invalid_value"],
                individual=individual_one
        )

        # Invalid molecule_ontology
        self.assertRaises(serializers.ValidationError, self.create,
                id='experiment:2',
                library_strategy='Bisulfite-Seq',
                experiment_type='Chromatin Accessibility',
                molecule_ontology=[{"id": "some_id"}],
                individual=individual_one
        )

        # Invalid value in other_fields
        self.assertRaises(serializers.ValidationError, self.create,
                id='experiment:2',
                library_strategy='Bisulfite-Seq',
                experiment_type='Chromatin Accessibility',
                other_fields={"some_field": "value", "invalid_value": 42},
                individual=individual_one
        )

        # Missing individual or biosamples
        self.assertRaises(ValidationError, self.create,
                id='experiment:2',
                library_strategy='Bisulfite-Seq',
                experiment_type='Chromatin Accessibility'
        )
