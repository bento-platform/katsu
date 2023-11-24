from rest_framework.test import APITestCase

from chord_metadata_service.cleanup import run_all_cleanup
from chord_metadata_service.experiments import cleanup as ec
from chord_metadata_service.experiments.models import Experiment, ExperimentResult, Instrument
from chord_metadata_service.patients.cleanup import clean_individuals
from chord_metadata_service.patients.models import Individual
from chord_metadata_service.phenopackets import cleanup as pc
from chord_metadata_service.phenopackets.models import (
    Biosample,
    Diagnosis,
    GeneDescriptor,
    GenomicInterpretation,
    Interpretation,
    MetaData,
    Phenopacket,
    PhenotypicFeature,
    VariantInterpretation,
    VariationDescriptor,
)
from chord_metadata_service.phenopackets.tests.constants import (
    VALID_DISEASE_ONTOLOGY,
    VALID_GENE_DESCRIPTOR_1,
    VALID_PROCEDURE_1,
    VALID_VARIANT_DESCRIPTOR,
    VALID_META_DATA_1,
    valid_biosample_1,
    valid_biosample_2,
    valid_diagnosis,
    valid_genomic_interpretation,
    valid_interpretation,
    valid_variant_interpretation,
)
from chord_metadata_service.resources.cleanup import clean_resources
from chord_metadata_service.resources.models import Resource
from chord_metadata_service.resources.tests.constants import VALID_RESOURCE_1
from chord_metadata_service.experiments.tests.constants import (
    valid_instrument,
    valid_experiment_result,
    valid_experiment,
)
from chord_metadata_service.chord.tests.constants import (
    VALID_PROJECT_1,
    valid_dataset_1,
    valid_phenotypic_feature,
)
from chord_metadata_service.chord.models import Project, Dataset


class CleanUpIndividualsAndPhenopacketsTestCase(APITestCase):

    def setUp(self):
        # Copied from test_api_search

        self.project = Project.objects.create(**VALID_PROJECT_1)
        self.dataset = Dataset.objects.create(**valid_dataset_1(self.project))

        # Set up a dummy phenopacket

        self.individual, _ = Individual.objects.get_or_create(
            id='patient:1', sex='FEMALE',
            time_at_last_encounter={
                "age": {
                    "iso8601duration": "P25Y3M2D"
                }
            })

        self.biosample_1 = Biosample.objects.create(**valid_biosample_1(self.individual))
        self.biosample_2 = Biosample.objects.create(**valid_biosample_2(None, VALID_PROCEDURE_1))

        self.resource = Resource.objects.create(**VALID_RESOURCE_1)

        self.meta_data = MetaData.objects.create(**VALID_META_DATA_1)
        self.meta_data.resources.set([self.resource])

        self.phenopacket = Phenopacket.objects.create(
            id="phenopacket_id:1",
            subject=self.individual,
            meta_data=self.meta_data,
            dataset=self.dataset
        )

        self.phenopacket.biosamples.set([self.biosample_1, self.biosample_2])

        # GenomicInterpretation (Gene & Variant)
        self.gene_descriptor = GeneDescriptor.objects.create(**VALID_GENE_DESCRIPTOR_1)
        self.variant_descriptor = VariationDescriptor.objects.create(**VALID_VARIANT_DESCRIPTOR)
        self.variant_interpretation = VariantInterpretation.objects.create(
            **valid_variant_interpretation(self.variant_descriptor)
        )
        self.genomic_interpretation = GenomicInterpretation.objects.create(
            **valid_genomic_interpretation(self.gene_descriptor, self.variant_interpretation)
        )

        # Phenopacket.interpretations
        self.disease_ontology = VALID_DISEASE_ONTOLOGY
        self.diagnosis = Diagnosis.objects.create(**valid_diagnosis(self.disease_ontology))
        self.diagnosis.genomic_interpretations.set([self.genomic_interpretation])

        self.interpretation = Interpretation.objects.create(**valid_interpretation(self.diagnosis))
        self.phenopacket.interpretations.set([self.interpretation])

        # Phenopacket.phenotypic_features
        self.phenotypic_feature = PhenotypicFeature.objects.create(
            **valid_phenotypic_feature(phenopacket=self.phenopacket)
        )

        self.unlinked_phenotypic_feature = PhenotypicFeature.objects.create(
            **valid_phenotypic_feature(phenopacket=None)
        )

    async def _check_dataset_delete(self, delete_url: str):
        # Check individual exists pre-table-delete
        await Individual.objects.aget(id="patient:1")

        # Check we can run clean_biosamples and clean_individuals with nothing lost (in order),
        # except the unlinked phenotypic feature,
        # since the individual is referenced by the phenopacket and the biosample is in use.
        self.assertEqual(await pc.clean_biosamples(), 0)
        self.assertEqual(await pc.clean_phenotypic_features(), 1)
        self.assertEqual(await clean_individuals(), 0)
        self.assertEqual(await clean_resources(), 0)

        r = await self.async_client.delete(delete_url)
        assert r.status_code == 204

        with self.assertRaises(PhenotypicFeature.DoesNotExist):  # PhenotypicFeature successfully deleted
            await self.phenotypic_feature.arefresh_from_db()

        with self.assertRaises(PhenotypicFeature.DoesNotExist):  # PhenotypicFeature successfully deleted
            await self.unlinked_phenotypic_feature.arefresh_from_db()

        self.assertEqual(await pc.clean_biosamples(), 0)
        self.assertEqual(await pc.clean_phenotypic_features(), 0)
        self.assertEqual(await clean_individuals(), 0)
        self.assertEqual(await clean_resources(), 0)

        with self.assertRaises(Individual.DoesNotExist):
            await Individual.objects.aget(id="patient:1")

        # Check we can run all cleaning again with no change...
        self.assertEqual(await run_all_cleanup(), 0)

    async def test_no_cleanup(self):
        await self.unlinked_phenotypic_feature.arefresh_from_db()

        # No cleanup except the unlinked phenotypic feature should occur without removing the dataset/phenopacket first
        self.assertEqual(await run_all_cleanup(), 1)

        with self.assertRaises(PhenotypicFeature.DoesNotExist):
            await self.unlinked_phenotypic_feature.arefresh_from_db()

    async def test_cleanup_basic(self):
        # Delete dataset to remove the parent phenopacket
        await self.dataset.adelete()

        # 1 metadata object +
        # 2 biosamples +
        # 0 linked phenotypic feature (removed via cascade with v2.17.0 database changes) +
        # 1 unlinked phenotypic feature (pretend left-over from pre v2.17.0 or created manually) +
        # 1 individual +
        # 0 experiment results +
        # 0 instruments +
        # 1 resource +
        # 1 interpretation +
        # 1 diagnosis
        # 1 genomic interpretation
        # = 9 objects total
        self.assertEqual(await run_all_cleanup(), 9)

        # Should have been removed via cascade with v2.17.0 database changes
        with self.assertRaises(PhenotypicFeature.DoesNotExist):
            await self.phenotypic_feature.arefresh_from_db()


class CleanUpExperimentsTestCase(APITestCase):

    def setUp(self):
        # Copied from test_api_search

        self.project = Project.objects.create(**VALID_PROJECT_1)
        self.dataset = Dataset.objects.create(**valid_dataset_1(self.project))

        # Set up a dummy phenopacket

        self.individual, _ = Individual.objects.get_or_create(
            id='patient:1', sex='FEMALE',
            time_at_last_encounter={
                "age": {
                    "iso8601duration": "P25Y3M2D"
                }
            })

        self.biosample_1 = Biosample.objects.create(**valid_biosample_1(self.individual))

        # add Experiments metadata and link to self.biosample_1
        self.instrument = Instrument.objects.create(**valid_instrument())
        self.experiment_result = ExperimentResult.objects.create(**valid_experiment_result())
        self.experiment = Experiment.objects.create(**valid_experiment(
            biosample=self.biosample_1, instrument=self.instrument, dataset=self.dataset))
        self.experiment.experiment_results.set([self.experiment_result])

    async def test_experiment_deletion(self):
        # Check we can run clean_biosamples, and clean_individuals with nothing lost (in order),
        # since the biosample is referenced by the experiment, references the individual, and uses the procedure.
        self.assertEqual(await pc.clean_biosamples(), 0)
        self.assertEqual(await clean_individuals(), 0)

        # Check we can run clean_experiment_results and clean_instruments safely with nothing lost, since they are
        # used by / reference the experiment.
        self.assertEqual(await ec.clean_experiment_results(), 0)
        self.assertEqual(await ec.clean_instruments(), 0)

        r = await self.async_client.delete(f'/api/datasets/{self.dataset.identifier}')
        assert r.status_code == 204

        with self.assertRaises(Experiment.DoesNotExist):
            await self.experiment.arefresh_from_db()

        with self.assertRaises(ExperimentResult.DoesNotExist):  # ExperimentResult successfully deleted
            await self.experiment_result.arefresh_from_db()

        with self.assertRaises(Instrument.DoesNotExist):  # Instrument successfully deleted
            await self.instrument.arefresh_from_db()

        with self.assertRaises(Biosample.DoesNotExist):  # Biosample successfully deleted
            await self.biosample_1.arefresh_from_db()

        self.assertEqual(await pc.clean_biosamples(), 0)
        self.assertEqual(await ec.clean_experiment_results(), 0)
        self.assertEqual(await ec.clean_instruments(), 0)
        self.assertEqual(await clean_individuals(), 0)

        with self.assertRaises(Individual.DoesNotExist):
            await Individual.objects.aget(id="patient:1")

        # Check we can run all cleaning again with no change...
        self.assertEqual(await run_all_cleanup(), 0)

    async def test_cleanup_basic(self):
        # Delete dataset to remove the parent phenopacket
        await self.dataset.adelete()

        # 1 biosample +
        # 1 individual +
        # 1 experiment result +
        # 1 instrument +
        # = 4 objects total
        self.assertEqual(await run_all_cleanup(), 4)
