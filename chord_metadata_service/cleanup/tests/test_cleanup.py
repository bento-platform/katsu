import uuid

from rest_framework.test import APITestCase

from django.urls import reverse

from chord_metadata_service.cleanup import run_all_cleanup
from chord_metadata_service.experiments import cleanup as ec
from chord_metadata_service.experiments.models import Experiment, ExperimentResult, Instrument
from chord_metadata_service.patients.cleanup import clean_individuals
from chord_metadata_service.patients.models import Individual
from chord_metadata_service.phenopackets import cleanup as pc
from chord_metadata_service.phenopackets.models import Biosample, MetaData, Phenopacket, Procedure, PhenotypicFeature
from chord_metadata_service.phenopackets.tests.constants import (
    VALID_PROCEDURE_1,
    valid_biosample_1,
    valid_biosample_2,
    VALID_META_DATA_1,
)
from chord_metadata_service.resources.cleanup import clean_resources
from chord_metadata_service.resources.models import Resource
from chord_metadata_service.resources.tests.constants import VALID_RESOURCE_1
from chord_metadata_service.experiments.tests.constants import (
    valid_instrument,
    valid_experiment_result,
    valid_experiment,
)
from chord_metadata_service.chord.data_types import DATA_TYPE_EXPERIMENT
from chord_metadata_service.chord.tests.constants import (
    VALID_PROJECT_1,
    valid_dataset_1,
    valid_table_1,
    valid_phenotypic_feature,
)
from chord_metadata_service.chord.models import Project, Dataset, TableOwnership, Table


class CleanUpIndividualsAndPhenopacketsTestCase(APITestCase):

    def setUp(self):
        # Copied from test_api_search

        self.project = Project.objects.create(**VALID_PROJECT_1)
        self.dataset = Dataset.objects.create(**valid_dataset_1(self.project))
        to, tr = valid_table_1(self.dataset.identifier, model_compatible=True)
        TableOwnership.objects.create(**to)
        self.table = Table.objects.create(**tr)

        # Set up a dummy phenopacket

        self.individual, _ = Individual.objects.get_or_create(
            id='patient:1', sex='FEMALE', age={"age": "P25Y3M2D"})

        self.procedure = Procedure.objects.create(**VALID_PROCEDURE_1)

        self.biosample_1 = Biosample.objects.create(**valid_biosample_1(self.individual, self.procedure))
        self.biosample_2 = Biosample.objects.create(**valid_biosample_2(None, self.procedure))

        self.resource = Resource.objects.create(**VALID_RESOURCE_1)

        self.meta_data = MetaData.objects.create(**VALID_META_DATA_1)
        self.meta_data.resources.set([self.resource])

        self.phenopacket = Phenopacket.objects.create(
            id="phenopacket_id:1",
            subject=self.individual,
            meta_data=self.meta_data,
            table=self.table
        )

        self.phenopacket.biosamples.set([self.biosample_1, self.biosample_2])

        self.phenotypic_feature = PhenotypicFeature.objects.create(
            **valid_phenotypic_feature(phenopacket=self.phenopacket)
        )

        self.unlinked_phenotypic_feature = PhenotypicFeature.objects.create(
            **valid_phenotypic_feature(phenopacket=None)
        )

    def _check_table_delete(self, delete_url: str):
        # Check individual exists pre-table-delete
        Individual.objects.get(id="patient:1")

        # Check we can run clean_biosamples and clean_individuals with nothing lost (in order),
        # except the unlinked phenotypic feature,
        # since the individual is referenced by the phenopacket and the biosample is in use.
        self.assertEqual(pc.clean_biosamples(), 0)
        self.assertEqual(pc.clean_phenotypic_features(), 1)
        self.assertEqual(pc.clean_procedures(), 0)
        self.assertEqual(clean_individuals(), 0)
        self.assertEqual(clean_resources(), 0)

        r = self.client.delete(delete_url)
        assert r.status_code == 204

        with self.assertRaises(Table.DoesNotExist):  # Table successfully deleted
            self.table.refresh_from_db()

        with self.assertRaises(PhenotypicFeature.DoesNotExist):  # PhenotypicFeature successfully deleted
            self.phenotypic_feature.refresh_from_db()

        with self.assertRaises(PhenotypicFeature.DoesNotExist):  # PhenotypicFeature successfully deleted
            self.unlinked_phenotypic_feature.refresh_from_db()

        self.assertEqual(pc.clean_biosamples(), 0)
        self.assertEqual(pc.clean_phenotypic_features(), 0)
        self.assertEqual(pc.clean_procedures(), 0)
        self.assertEqual(clean_individuals(), 0)
        self.assertEqual(clean_resources(), 0)

        with self.assertRaises(Individual.DoesNotExist):
            Individual.objects.get(id="patient:1")

        # Check we can run all cleaning again with no change...
        self.assertEqual(run_all_cleanup(), 0)

    def test_no_cleanup(self):
        self.unlinked_phenotypic_feature.refresh_from_db()

        # No cleanup except the unlinked phenotypic feature should occur without removing the table/phenopacket first
        self.assertEqual(run_all_cleanup(), 1)

        with self.assertRaises(PhenotypicFeature.DoesNotExist):
            self.unlinked_phenotypic_feature.refresh_from_db()

    def test_cleanup_basic(self):
        # Delete table to remove the parent phenopacket
        self.table.ownership_record.delete()

        # 1 metadata object +
        # 2 biosamples +
        # 1 procedure +
        # 0 linked phenotypic feature (removed via cascade with v2.17.0 database changes) +
        # 1 unlinked phenotypic feature (pretend left-over from pre v2.17.0 or created manually) +
        # 1 individual +
        # 0 experiment results +
        # 0 instruments +
        # 1 resource
        # = 7 objects total
        self.assertEqual(run_all_cleanup(), 7)

        # Should have been removed via cascade with v2.17.0 database changes
        with self.assertRaises(PhenotypicFeature.DoesNotExist):
            self.phenotypic_feature.refresh_from_db()

    def test_cleanup_api_table_delete(self):
        # This reverse points to the API table delete, not the /tables/<...> delete in views_search
        self._check_table_delete(reverse("table-detail", args=[self.table.ownership_record_id]))

    def test_cleanup_chord_table_delete(self):
        self._check_table_delete(f"/tables/{self.table.ownership_record_id}")


class CleanUpExperimentsTestCase(APITestCase):

    def setUp(self):
        # Copied from test_api_search

        self.project = Project.objects.create(**VALID_PROJECT_1)
        self.dataset = Dataset.objects.create(**valid_dataset_1(self.project))

        # Set up a dummy phenopacket

        self.individual, _ = Individual.objects.get_or_create(
            id='patient:1', sex='FEMALE', age={"age": "P25Y3M2D"})

        self.procedure = Procedure.objects.create(**VALID_PROCEDURE_1)

        self.biosample_1 = Biosample.objects.create(**valid_biosample_1(self.individual, self.procedure))

        # table for experiments metadata
        self.to_exp = TableOwnership.objects.create(table_id=uuid.uuid4(), service_id=uuid.uuid4(),
                                                    service_artifact="experiments", dataset=self.dataset)
        self.t_exp = Table.objects.create(ownership_record=self.to_exp, name="Table 2", data_type=DATA_TYPE_EXPERIMENT)

        # add Experiments metadata and link to self.biosample_1
        self.instrument = Instrument.objects.create(**valid_instrument())
        self.experiment_result = ExperimentResult.objects.create(**valid_experiment_result())
        self.experiment = Experiment.objects.create(**valid_experiment(
            biosample=self.biosample_1, instrument=self.instrument, table=self.t_exp))
        self.experiment.experiment_results.set([self.experiment_result])

    def test_experiment_deletion(self):
        # Check we can run clean_biosamples, clean_procedures, and clean_individuals with nothing lost (in order),
        # since the biosample is referenced by the experiment, references the individual, and uses the procedure.
        self.assertEqual(pc.clean_biosamples(), 0)
        self.assertEqual(pc.clean_procedures(), 0)
        self.assertEqual(clean_individuals(), 0)

        # Check we can run clean_experiment_results and clean_instruments safely with nothing lost, since they are
        # used by / reference the experiment.
        self.assertEqual(ec.clean_experiment_results(), 0)
        self.assertEqual(ec.clean_instruments(), 0)

        # Delete table ownership record + table record
        r = self.client.delete(reverse("table-detail", args=[self.t_exp.ownership_record_id]))
        assert r.status_code == 204

        with self.assertRaises(Table.DoesNotExist):  # Table successfully deleted
            self.t_exp.refresh_from_db()

        with self.assertRaises(ExperimentResult.DoesNotExist):  # ExperimentResult successfully deleted
            self.experiment_result.refresh_from_db()

        with self.assertRaises(Instrument.DoesNotExist):  # Instrument successfully deleted
            self.instrument.refresh_from_db()

        with self.assertRaises(Biosample.DoesNotExist):  # Biosample successfully deleted
            self.biosample_1.refresh_from_db()

        self.assertEqual(pc.clean_biosamples(), 0)
        self.assertEqual(pc.clean_procedures(), 0)
        self.assertEqual(ec.clean_experiment_results(), 0)
        self.assertEqual(ec.clean_instruments(), 0)
        self.assertEqual(clean_individuals(), 0)

        with self.assertRaises(Individual.DoesNotExist):
            Individual.objects.get(id="patient:1")

        # Check we can run all cleaning again with no change...
        self.assertEqual(run_all_cleanup(), 0)

    def test_cleanup_basic(self):
        # Delete table to remove the parent phenopacket
        self.t_exp.ownership_record.delete()

        # 1 biosample +
        # 1 procedure +
        # 1 individual +
        # 1 experiment result +
        # 1 instrument +
        # = 5 objects total
        self.assertEqual(run_all_cleanup(), 5)
