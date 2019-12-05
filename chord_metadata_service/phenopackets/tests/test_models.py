from django.test import TestCase
from ..models import *
from chord_metadata_service.patients.models import Individual
from django.db.utils import IntegrityError
from django.core.exceptions import ValidationError
from .constants import *


class BiosampleTest(TestCase):
	""" Test module for Biosample model """

	def setUp(self):
		self.individual = Individual.objects.create(**VALID_INDIVIDUAL_1)
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
		self.biosample_1 = Biosample.objects.create(**valid_biosample_1(
			self.individual_1, self.procedure)
		)
		self.biosample_2 = Biosample.objects.create(**valid_biosample_2(
			self.individual_2, self.procedure)
		)
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
				**valid_phenotypic_feature(
					biosample=self.biosample_2,
					phenopacket=self.phenopacket)
					)

	def test_phenotypic_feature(self):
		phenotypic_feature_query = PhenotypicFeature.objects.filter(
			severity__label='Mild',
			pftype__label='Proptosis'
			)
		phenotypic_feature_2 = PhenotypicFeature.objects.get(
			id=2, phenopacket__id='phenopacket_id:1'
			)
		self.assertEqual(PhenotypicFeature.objects.count(), 2)
		self.assertEqual(phenotypic_feature_query.count(), 2)
		self.assertEqual(phenotypic_feature_2.biosample.id, 'biosample_id:2')


class ProcedureTest(TestCase):

	def setUp(self):
		self.procedure_1 = Procedure.objects.create(**VALID_PROCEDURE_1)
		self.procedure_1 = Procedure.objects.create(**VALID_PROCEDURE_2)

	def test_procedure(self):
		procedure_query_1 = Procedure.objects.filter(
			body_site__label__icontains='arm'
			)
		procedure_query_2 = Procedure.objects.filter(code__id='NCIT:C28743')
		self.assertEqual(procedure_query_1.count(), 2)
		self.assertEqual(procedure_query_2.count(), 2)


class HtsFileTest(TestCase):

	def setUp(self):
		self.hts_file = HtsFile.objects.create(**VALID_HTS_FILE)

	def test_hts_file(self):
		hts_file = HtsFile.objects.get(genome_assembly='GRCh38')
		self.assertEqual(hts_file.uri, 'https://data.example/genomes/germline_wgs.vcf.gz')


class GeneTest(TestCase):

	def setUp(self):
		self.gene_1 = Gene.objects.create(**VALID_GENE_1)
		

	def test_gene(self):
		gene_1 = Gene.objects.get(id='HGNC:347')
		self.assertEqual(gene_1.symbol, 'ETF1')		
		with self.assertRaises(IntegrityError):
			Gene.objects.create(**DUPLICATE_GENE_2)


class VariantTest(TestCase):

	def setUp(self):
		self.variant = Variant.objects.create(**VALID_VARIANT_1)

	def test_variant(self):
		variant_query = Variant.objects.filter(zygosity__id='NCBITaxon:9606')
		self.assertEqual(variant_query.count(), 1)


class DiseaseTest(TestCase):

	def setUp(self):
		self.disease_1 = Disease.objects.create(**VALID_DISEASE_1)

	def test_disease(self):
		disease_query = Disease.objects.filter(term__id='OMIM:164400')
		self.assertEqual(disease_query.count(), 1)


class GenomicInterpretationTest(TestCase):

	def setUp(self):
		self.gene = Gene.objects.create(**VALID_GENE_1)
		self.variant = Variant.objects.create(**VALID_VARIANT_1)
		self.genomic_interpretation = GenomicInterpretation.objects.create(
			**valid_genomic_interpretation(self.gene, self.variant)
			)

	def test_genomic_interpretation(self):
		genomic_interpretation_query = GenomicInterpretation.objects.filter(
			gene='HGNC:347')
		self.assertEqual(genomic_interpretation_query.count(), 1)
		self.assertEqual(GenomicInterpretation.objects.count(), 1)

	def test_validation_gene_or_variant(self):
		with self.assertRaises(ValidationError):
			test = GenomicInterpretation.objects.create(
			**valid_genomic_interpretation()
			).clean()


class DiagnosisTest(TestCase):

	def setUp(self):
		self.disease = Disease.objects.create(**VALID_DISEASE_1)

		self.gene = Gene.objects.create(**VALID_GENE_1)
		self.variant = Variant.objects.create(**VALID_VARIANT_1)
		self.genomic_interpretation_1 = GenomicInterpretation.objects.create(
			**valid_genomic_interpretation(self.gene, self.variant)
			)
		self.genomic_interpretation_2 = GenomicInterpretation.objects.create(
			**valid_genomic_interpretation(self.gene)
			)
		self.diagnosis = Diagnosis.objects.create(**valid_diagnosis(
			self.disease))
		self.diagnosis.genomic_interpretations.set([
			self.genomic_interpretation_1,
			self.genomic_interpretation_2
			])

	def test_diagnosis(self):
		diagnosis = Diagnosis.objects.filter(disease__term__id='OMIM:164400')
		self.assertEqual(diagnosis.count(), 1)


class InterpretationTest(TestCase):

	def setUp(self):
		self.meta_data_phenopacket = MetaData.objects.create(**VALID_META_DATA_1)
		self.meta_data_interpretation = MetaData.objects.create(**VALID_META_DATA_2)

		self.individual = Individual.objects.create(**VALID_INDIVIDUAL_1)
		self.phenopacket = Phenopacket.objects.create(
			id="phenopacket_id:1",
			subject=self.individual,
			meta_data=self.meta_data_phenopacket,
		)
		self.interpretation = Interpretation.objects.create(**valid_interpretation(
			phenopacket=self.phenopacket,
			meta_data=self.meta_data_interpretation
			))

	def test_interpretation(self):
		interpretation_query = Interpretation.objects.filter(
			resolution_status='IN_PROGRESS'
			)
		self.assertEqual(interpretation_query.count(), 1)


class ResourceTest(TestCase):

	def setUp(self):
		self.resource_1 = Resource.objects.create(**VALID_RESOURCE_1)
		self.resource_2 = Resource.objects.create(**VALID_RESOURCE_2)

	def test_resource(self):
		self.assertEqual(Resource.objects.count(), 2)
		with self.assertRaises(IntegrityError):
			Resource.objects.create(**DUPLICATE_RESOURCE_3)


class MetaDataTest(TestCase):

	def setUp(self):
		self.resource_1 = Resource.objects.create(**VALID_RESOURCE_1)
		self.resource_2 = Resource.objects.create(**VALID_RESOURCE_2)
		self.metadata = MetaData.objects.create(**VALID_META_DATA_2)
		self.metadata.resources.set([self.resource_1, self.resource_2])

	def test_metadata(self):
		metadata = MetaData.objects.get(created_by__icontains='ksenia')
		self.assertEqual(metadata.submitted_by, 'Ksenia Zaytseva')
		self.assertEqual(metadata.resources.count(), 2)
