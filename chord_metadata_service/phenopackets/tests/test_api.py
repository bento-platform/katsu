import json
from django.urls import include, path, reverse
from rest_framework import status
from rest_framework.test import APITestCase
from ..models import *
from chord_metadata_service.restapi.schemas import ONTOLOGY_CLASS
from .constants import *
from ..serializers import *
from rest_framework.test import APIClient


def get_response(viewname, obj):
	""" Generic POST function. """

	client = APIClient()
	response = client.post(
			reverse(viewname),
			data=json.dumps(obj),
			content_type='application/json'
		)
	return response


class CreateBiosampleTest(APITestCase):
	""" Test module for creating an Biosample. """

	def setUp(self):
		self.individual = Individual.objects.create(**VALID_INDIVIDUAL_1)
		self.procedure = VALID_PROCEDURE_1
		self.valid_payload = {
			"id": "biosample:1",
			"individual": self.individual.id,
			"procedure": self.procedure,
			"description": "This is a test description.",
			"sampled_tissue": {
				"id": "UBERON_0001256",
				"label": "wall of urinary bladder"
			},
			"individual_age_at_collection": "P67Y3M2D",
			"histological_diagnosis": {
				"id": "NCIT:C39853",
				"label": "Infiltrating Urothelial Carcinoma"
			},
			"tumor_progression": {
				"id": "NCIT:C84509",
				"label": "Primary Malignant Neoplasm"
			},
			"tumor_grade": {
				"id": "NCIT:C48766",
				"label": "pT2b Stage Finding"
			},
			"diagnostic_markers": [
				{
					"id": "NCIT:C49286",
					"label": "Hematology Test"
				},
				{
					"id": "NCIT:C15709",
					"label": "Genetic Testing"
				}
			]
		}
		self.invalid_payload = {
			"id": "biosample:1",
			"individual": self.individual.id,
			"procedure": self.procedure,
			"description": "This is a test description.",
			"sampled_tissue": {
				"id": "UBERON_0001256"
			},
			"individual_age_at_collection": "P67Y3M2D",
			"histological_diagnosis": {
				"id": "NCIT:C39853",
				"label": "Infiltrating Urothelial Carcinoma"
			},
			"tumor_progression": {
				"id": "NCIT:C84509",
				"label": "Primary Malignant Neoplasm"
			},
			"tumor_grade": {
				"id": "NCIT:C48766",
				"label": "pT2b Stage Finding"
			},
			"diagnostic_markers": [
				{
					"id": "NCIT:C49286",
					"label": "Hematology Test"
				},
				{
					"id": "NCIT:C15709",
					"label": "Genetic Testing"
				}
			]
		}

	def test_create_biosample(self):
		""" POST a new biosample. """

		response = get_response('biosample-list', self.valid_payload)
		self.assertEqual(response.status_code, status.HTTP_201_CREATED)
		self.assertEqual(Biosample.objects.count(), 1)
		self.assertEqual(Biosample.objects.get().id, 'biosample:1')

	def test_create_invalid_biosample(self):
		""" POST a new biosample with invalid data. """

		invalid_response = get_response('biosample-list', self.invalid_payload)
		self.assertEqual(
			invalid_response.status_code, status.HTTP_400_BAD_REQUEST)
		self.assertEqual(Biosample.objects.count(), 0)

	def test_seriliazer_validate_invalid(self):
		serializer = BiosampleSerializer(data=self.invalid_payload)
		self.assertEqual(serializer.is_valid(), False)

	def test_seriliazer_validate_valid(self):
		serializer = BiosampleSerializer(data=self.valid_payload)
		self.assertEqual(serializer.is_valid(), True)


class CreatePhenotypicFeatureTest(APITestCase):

	def setUp(self):
		valid_payload = valid_phenotypic_feature()
		removed_pftype = valid_payload.pop('pftype', None)
		valid_payload['type'] = {
					"id": "HP:0000520",
					"label": "Proptosis"
				}
		self.valid_phenotypic_feature = valid_payload
		invalid_payload = invalid_phenotypic_feature()
		invalid_payload['type'] = {
					"id": "HP:0000520",
					"label": "Proptosis"
				}
		self.invalid_phenotypic_feature = invalid_payload
		

	def test_create_phenotypic_feature(self):
		""" POST a new phenotypic feature. """

		response = get_response('phenotypicfeature-list', self.valid_phenotypic_feature)
		self.assertEqual(response.status_code, status.HTTP_201_CREATED)
		self.assertEqual(PhenotypicFeature.objects.count(), 1)

	def test_modifier(self):
		serializer = PhenotypicFeatureSerializer(data=self.invalid_phenotypic_feature)
		self.assertEqual(serializer.is_valid(), False)


class CreateProcedureTest(APITestCase):

	def setUp(self):
		self.valid_procedure = VALID_PROCEDURE_1
		self.duplicate_procedure = VALID_PROCEDURE_1
		self.valid_procedure_duplicate_code = VALID_PROCEDURE_2

	def test_procedure(self):
		response = get_response('procedure-list', self.valid_procedure)
		response_duplicate = get_response(
			'procedure-list', self.duplicate_procedure)
		response_duplicate_code = get_response(
			'procedure-list', self.valid_procedure_duplicate_code)
		self.assertEqual(response.status_code, status.HTTP_201_CREATED)
		self.assertEqual(response_duplicate.status_code, status.HTTP_400_BAD_REQUEST)
		self.assertEqual(Procedure.objects.count(), 2)


class CreateHtsFileTest(APITestCase):

	def setUp(self):
		self.hts_file = VALID_HTS_FILE

	def test_hts_file(self):
		response = get_response('htsfile-list', self.hts_file)
		self.assertEqual(response.status_code, status.HTTP_201_CREATED)
		self.assertEqual(HtsFile.objects.count(), 1)


class CreateGeneTest(APITestCase):

	def setUp(self):
		self.gene = VALID_GENE_1
		self.duplicate_gene = DUPLICATE_GENE_2
		self.invalid_gene = INVALID_GENE_2

	def test_gene(self):
		response = get_response('gene-list', self.gene)
		response_duplicate = get_response('htsfile-list', self.duplicate_gene)
		self.assertEqual(response.status_code, status.HTTP_201_CREATED)
		self.assertEqual(response_duplicate.status_code, status.HTTP_400_BAD_REQUEST)
		self.assertEqual(Gene.objects.count(), 1)

	def test_alternate_ids(self):
		serializer = GeneSerializer(data=self.invalid_gene)
		self.assertEqual(serializer.is_valid(), False)


class CreateVariantTest(APITestCase):

	def setUp(self):
		self.variant = VALID_VARIANT_1
		self.variant_2 = VALID_VARIANT_2

	def test_variant(self):
		response = get_response('variant-list', self.variant)
		serializer = VariantSerializer(data=self.variant)
		self.assertEqual(serializer.is_valid(), True)
		self.assertEqual(response.status_code, status.HTTP_201_CREATED)
		self.assertEqual(Variant.objects.count(), 1)

	def test_to_represenation(self):
		response = get_response('variant-list', self.variant_2)
		serializer = VariantSerializer(data=self.variant)
		self.assertEqual(serializer.is_valid(), True)
		self.assertEqual(response.status_code, status.HTTP_201_CREATED)
		self.assertEqual(Variant.objects.count(), 1)


class CreateDiseaseTest(APITestCase):

	def setUp(self):
		self.disease = VALID_DISEASE_1
		self.invalid_disease = INVALID_DISEASE_2

	def test_disease(self):
		response = get_response('disease-list', self.disease)
		serializer = DiseaseSerializer(data=self.disease)
		self.assertEqual(serializer.is_valid(), True)
		self.assertEqual(response.status_code, status.HTTP_201_CREATED)
		self.assertEqual(Disease.objects.count(), 1)

	def test_invalid_disease(self):
		serializer = DiseaseSerializer(data=self.invalid_disease)
		self.assertEqual(serializer.is_valid(), False)
		self.assertEqual(Disease.objects.count(), 0)


class CreateResourceTest(APITestCase):

	def setUp(self):
		self.resource = VALID_RESOURCE_2
		self.duplicate_resource = DUPLICATE_RESOURCE_3

	def test_resource(self):
		response = get_response('resource-list', self.resource)
		self.assertEqual(response.status_code, status.HTTP_201_CREATED)
		self.assertEqual(Resource.objects.count(), 1)

	def test_serializer(self):
		serializer = ResourceSerializer(data=self.resource)
		self.assertEqual(serializer.is_valid(), True)


class CreateMetaDataTest(APITestCase):

	def setUp(self):
		self.metadata = VALID_META_DATA_1

	def test_resource(self):
		response = get_response('metadata-list', self.metadata)
		self.assertEqual(response.status_code, status.HTTP_201_CREATED)
		self.assertEqual(MetaData.objects.count(), 1)

	def test_serializer(self):
		serializer = MetaDataSerializer(data=self.metadata)
		self.assertEqual(serializer.is_valid(), True)

