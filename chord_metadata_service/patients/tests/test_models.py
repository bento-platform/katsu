from chord_metadata_service.chord.tests.helpers import ProjectTestCase
from chord_metadata_service.phenopackets.tests import constants as c
from chord_metadata_service.phenopackets import models as m
from chord_metadata_service.restapi.models import SchemaType

from ..models import Individual
from ..filters import IndividualFilter


class IndividualTest(ProjectTestCase):
    """ Test module for Individual model """

    def setUp(self):
        self.individual_one = Individual.objects.create(id='patient:1', sex='FEMALE')
        self.individual_two = Individual.objects.create(id='patient:2', sex='FEMALE')
        self.diseases = [
            m.Disease.objects.create(**c.VALID_DISEASE_1),
            m.Disease.objects.create(**c.INVALID_DISEASE_2),
        ]
        self.meta_data = m.MetaData.objects.create(**c.VALID_META_DATA_1)
        self.phenopacket = m.Phenopacket.objects.create(
            id="phenopacket_id:1",
            subject=self.individual_one,
            meta_data=self.meta_data,
            dataset=self.dataset
        )
        self.phenopacket.diseases.set(self.diseases)
        self.phenotypic_feature_1 = m.PhenotypicFeature.objects.create(
            **c.valid_phenotypic_feature(phenopacket=self.phenopacket)
        )
        self.phenotypic_feature_2 = m.PhenotypicFeature.objects.create(
            **c.valid_phenotypic_feature(phenopacket=self.phenopacket)
        )

    def test_individual(self):
        individual_one = Individual.objects.get(id='patient:1')
        individual_two = Individual.objects.get(id='patient:2')
        self.assertEqual(individual_one.sex, 'FEMALE')
        number_of_pf_one = len(m.PhenotypicFeature.objects.filter(phenopacket__subject=individual_one))
        self.assertEqual(number_of_pf_one, 2)
        number_of_pf_two = len(m.PhenotypicFeature.objects.filter(phenopacket__subject=individual_two))
        self.assertEqual(number_of_pf_two, 0)
        self.assertEqual(individual_one.schema_type, SchemaType.INDIVIDUAL)
        self.assertEqual(individual_one.get_project_id(), self.project.identifier)

    def test_filtering(self):
        f = IndividualFilter()
        # all phenotypic feature constants have excluded=True
        result = f.filter_found_phenotypic_feature(Individual.objects.all(), "phenopackets", "proptosis")
        self.assertEqual(len(result), 0)
        result = f.filter_found_phenotypic_feature(Individual.objects.all(), "phenopackets", "HP:0000520")
        self.assertEqual(len(result), 0)

        # There are 2 excluded phenotypic features...
        result = Individual.objects.all().filter(phenopackets__phenotypic_features__excluded=True)
        self.assertEqual(len(result), 2)

        # ... and both excluded phenotypic features are for individual_one
        result = result.distinct()
        self.assertEqual(len(result), 1)
        self.assertEqual(result.first().id, self.individual_one.id)

        result = f.filter_disease(Individual.objects.all(), "phenopackets", c.VALID_DISEASE_1["term"]["id"])
        self.assertEqual(len(result), 1)
        result = f.filter_disease(Individual.objects.all(), "phenopackets", c.VALID_DISEASE_1["term"]["label"])
        self.assertEqual(len(result), 1)
