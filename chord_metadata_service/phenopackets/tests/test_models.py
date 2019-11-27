from django.test import TestCase
from ..models import Biosample, MetaData, Procedure, Phenopacket
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
