from django.test import TransactionTestCase

from chord_metadata_service.authz.tests.helpers import PermissionsTestCaseMixin
from chord_metadata_service.experiments import models as exp_m
from chord_metadata_service.experiments.tests import constants as exp_c
from chord_metadata_service.patients import models as pa_m
from chord_metadata_service.phenopackets import models as ph_m
from chord_metadata_service.phenopackets.tests import constants as ph_c

from ..pydantic_models import BinWithValue
from ..stats import individual_biosample_tissue_stats, individual_experiment_type_stats


class IndividualPublicStatsTest(TransactionTestCase, PermissionsTestCaseMixin):

    def setUp(self):
        # create 2 phenopackets for 2 individuals; each individual has 1 biosample;
        # one of phenopackets has 1 phenotypic feature and 1 disease
        self.individual_1 = pa_m.Individual.objects.create(**ph_c.VALID_INDIVIDUAL_1)
        self.metadata_1 = ph_m.MetaData.objects.create(**ph_c.VALID_META_DATA_1)
        self.phenopacket_1 = ph_m.Phenopacket.objects.create(
            **ph_c.valid_phenopacket(subject=self.individual_1, meta_data=self.metadata_1)
        )
        self.biosample_1 = ph_m.Biosample.objects.create(**ph_c.valid_biosample_1(self.individual_1))
        self.phenopacket_1.biosamples.set([self.biosample_1])

        # experiments
        self.instrument = exp_m.Instrument.objects.create(**exp_c.valid_instrument())
        self.experiment = exp_m.Experiment.objects.create(**exp_c.valid_experiment(self.biosample_1, self.instrument))
        self.experiment_result = exp_m.ExperimentResult.objects.create(**exp_c.valid_experiment_result())
        self.experiment.experiment_results.set([self.experiment_result])

    async def test_individual_biosample_tissue_stats(self):
        count, res = await individual_biosample_tissue_stats(
            pa_m.Individual.objects.all(), None, self.permissions_full)
        self.assertEqual(count, 1)
        self.assertListEqual(res.root, [BinWithValue(label="wall of urinary bladder", value=1)])

    async def individual_experiment_type_stats(self):
        count, res = await individual_experiment_type_stats(
            pa_m.Individual.objects.all(), None, self.permissions_full)
        self.assertEqual(count, 1)
        self.assertListEqual(res.root, [BinWithValue(label="DNA Methylation", value=1)])
