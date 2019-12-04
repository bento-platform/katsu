from django.test import TestCase
from ..models import Biosample, MetaData, Procedure, Phenopacket, PhenotypicFeature
from chord_metadata_service.patients.models import Individual

from .constants import *


class BiosampleTest(TestCase):
	""" Test module for Biosample model """

	def setUp(self):
		self.individual, _ = Individual.objects.get_or_create(
			id='patient:1', sex='FEMALE', age='P25Y3M2D')

		self.procedure = Procedure.objects.create(**VALID_PROCEDURE_1)

		self.biosample_1 = Biosample.objects.create(**valid_biosample_1(self.individual, self.procedure))
		self.biosample_2 = Biosample.objects.create(**valid_biosample_2(None, self.procedure))

		self.meta_data = MetaData.objects.create(**VALID_META_DATA_1)

		self.phenopacket = Phenopacket.objects.create(
			id="phenopacket_id:1",
			subject=self.individual,
			meta_data=self.meta_data,
		)

		self.phenopacket.biosamples.set([self.biosample_1, self.biosample_2])

	def test_biosample(self):
		biosample_one = Biosample.objects.get(
			tumor_progression__label='Primary Malignant Neoplasm',
			sampled_tissue__label__icontains='urinary bladder'
			)
		self.assertEqual(biosample_one.id, 'biosample_id:1')

	def test_string_representations(self):
		# Test __str__
		self.assertEqual(str(self.individual), str(self.individual.pk))
		self.assertEqual(str(self.procedure), str(self.procedure.pk))
		self.assertEqual(str(self.biosample_1), str(self.biosample_1.pk))
		self.assertEqual(str(self.meta_data), str(self.meta_data.pk))
		self.assertEqual(str(self.phenopacket), str(self.phenopacket.pk))


class PhenotypicFeatureTest(TestCase):
	""" Test module for PhenotypicFeature model. """

	def setUp(self):
		self.individual_1 = Individual.objects.create(**VALID_INDIVIDUAL_1)
		self.individual_2 = Individual.objects.create(**VALID_INDIVIDUAL_2)
		self.procedure = Procedure.objects.create(**VALID_PROCEDURE_1)
		self.biosample_1 = Biosample.objects.create(**valid_biosample_1(self.individual_1, self.procedure))
		self.biosample_2 = Biosample.objects.create(**valid_biosample_2(self.individual_2, self.procedure))
		self.meta_data = MetaData.objects.create(**VALID_META_DATA_1)
		self.phenopacket = Phenopacket.objects.create(
			id="phenopacket_id:1",
			subject=self.individual_2,
			meta_data=self.meta_data,
		)
		self.phenotypic_feature_1 = PhenotypicFeature.objects.create(
				**valid_phenotypic_feature(biosample=self.biosample_1)
			)
		self.phenotypic_feature_2 = PhenotypicFeature.objects.create(
				**valid_phenotypic_feature(biosample=self.biosample_2, phenopacket=self.phenopacket)
			)

	def test_phenotypic_feature(self):
		phenotypic_feature_query = PhenotypicFeature.objects.filter(
			severity__label='Mild',
			pftype__label='Proptosis'
			)
		self.assertEqual(PhenotypicFeature.objects.count(), 2)
		self.assertEqual(phenotypic_feature_query.count(), 2)

