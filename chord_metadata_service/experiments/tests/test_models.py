from django.test import TestCase
from rest_framework import serializers
from ..models import Experiment


class ExperimentTest(TestCase):
    """ Test module for Experiment model """

    def setUp(self):
        Experiment.objects.create(
            id='experiment:1',
            reference_registry_id='',
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
        self.assertRaises(serializers.ValidationError, self.create,
                id='experiment:2',
                library_strategy='Bisulfite-Seq',
                experiment_ontology=["invalid_value"],
        )

        self.assertRaises(serializers.ValidationError, self.create,
                id='experiment:2',
                library_strategy='Bisulfite-Seq',
                molecule_ontology=[{"id": "some_id"}],
        )

        self.assertRaises(serializers.ValidationError, self.create,
                id='experiment:2',
                library_strategy='Bisulfite-Seq',
                other_fields={"some_field": "value", "invalid_value": 42}
        )
