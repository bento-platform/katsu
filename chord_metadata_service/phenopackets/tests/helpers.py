from chord_metadata_service.chord.tests.helpers import ProjectTestCase
from chord_metadata_service.experiments.models import Experiment
from chord_metadata_service.phenopackets import models as m
from chord_metadata_service.phenopackets.tests import constants as c
from chord_metadata_service.experiments.tests import constants as exp_consts


class PhenoTestCase(ProjectTestCase):

    def setUp(self) -> None:
        self.individual = m.Individual.objects.create(**c.VALID_INDIVIDUAL_1)
        self.procedure = m.Procedure.objects.create(**c.VALID_PROCEDURE_1)
        self.biosample_1 = m.Biosample.objects.create(**c.valid_biosample_1(self.individual, self.procedure))
        self.biosample_2 = m.Biosample.objects.create(**c.valid_biosample_2(None, self.procedure))
        self.biosample_3 = m.Biosample.objects.create(**{
            **c.valid_biosample_2(None, self.procedure),
            "id": 'biosample_id:3'
        })
        self.meta_data = m.MetaData.objects.create(**c.VALID_META_DATA_1)
        self.phenopacket = m.Phenopacket.objects.create(
            id="phenopacket_id:1",
            subject=self.individual,
            meta_data=self.meta_data,
            dataset=self.dataset,
        )
        self.phenotypic_feature_1 = m.PhenotypicFeature.objects.create(
            **c.valid_phenotypic_feature(phenopacket=self.phenopacket)
        )
        self.phenotypic_feature_2 = m.PhenotypicFeature.objects.create(
            **c.valid_phenotypic_feature(phenopacket=self.phenopacket)
        )
        self.disease_1 = m.Disease.objects.create(**c.VALID_DISEASE_1)
        self.phenopacket.diseases.set([self.disease_1])
        self.phenopacket.biosamples.set([self.biosample_1, self.biosample_2])
        self.phenotypic_feature_1 = m.PhenotypicFeature.objects.create(
            **c.valid_phenotypic_feature(biosample=self.biosample_1))
        self.phenotypic_feature_2 = m.PhenotypicFeature.objects.create(
            **c.valid_phenotypic_feature(biosample=self.biosample_2, phenopacket=self.phenopacket))
        self.experiment = Experiment.objects.create(
            **exp_consts.valid_experiment(self.biosample_1, dataset=self.dataset),
        )
        return super().setUp()
