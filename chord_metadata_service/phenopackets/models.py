from django.db import models
from django.utils import timezone
from django.core.exceptions import ValidationError
from django.contrib.postgres.fields import JSONField, ArrayField
from elasticsearch_dsl import (
	Document, Text, Date, Search,
	Object, Boolean, InnerDoc, Nested)

from chord_metadata_service.patients.models import Individual
from .index import *
from django.db.models.signals import post_save, post_delete, pre_save
from django.dispatch import receiver


#############################################################
#                                                           #
#                        Metadata                           #
#                                                           #
#############################################################


class Resource(models.Model):
	"""
	Class to represent a description of an external resource
	used for referencing an object

	FHIR: CodeSystem
	"""

	# resource_id e.g. "id": "uniprot"
	resource_id = models.CharField(max_length=200,
		help_text='For OBO ontologies, the value of this string '
		'MUST always be the official OBO ID, which is always '
		'equivalent to the ID prefix in lower case. '
		'For other resources use the prefix in identifiers.org.')
	name = models.CharField(max_length=200,
		help_text='The full name of the ontology referred to by the id element.')
	namespace_prefix = models.CharField(max_length=200,
		help_text='The prefix used in the CURIE of an Ontology term.')
	url = models.URLField(max_length=200,
		help_text='For OBO ontologies, this MUST be the PURL. '
		'Other resources should link to the official or top-level url.')
	version = models.CharField(max_length=200,
		help_text='The version of the resource or ontology used to make the annotation.')
	iri_prefix = models.URLField(max_length=200,
		help_text='The full IRI prefix which can be used with the namespace_prefix '
		'and the Ontology::id to resolve to an IRI for a term.')

	def __str__(self):
		return str(self.id)


class MetaData(models.Model):
	"""
	Class to store structured definitions of the resources
	and ontologies used within the phenopacket

	FHIR: Metadata
	"""

	# CHECK !!! created or submitted?
	created = models.DateTimeField(default=timezone.now,
		help_text='Time when this object was created.')
	created_by = models.CharField(max_length=200,
		help_text='Name of person who created the phenopacket.')
	submitted_by = models.CharField(max_length=200, blank=True,
		help_text='Name of person who submitted the phenopacket.')
	resources = models.ManyToManyField(Resource,
		help_text='This element contains a listing of the ontologies/resources '
		'referenced in the phenopacket.')
	updates = ArrayField(JSONField(null=True, blank=True), blank=True, null=True,
		help_text='List of updates to the phenopacket.')
	phenopacket_schema_version = models.CharField(max_length=200, blank=True,
		help_text='Schema version of the current phenopacket.')
	external_references = ArrayField(JSONField(null=True, blank=True),
		blank=True, null=True,
		help_text='List of external resources from the phenopacket was derived.')

	def __str__(self):
		return str(self.id)


#############################################################


#############################################################
#                                                           #
#                  Phenotypic information                   #
#                                                           #
#############################################################


class PhenotypicFeature(models.Model):
	"""
	Class to describe a phenotype of an Individual

	FHIR: Condition or Observation
	"""

	description = models.CharField(max_length=200, blank=True,
		help_text='Human-readable verbiage NOT for structured text')
	pftype = JSONField(verbose_name='type',
		help_text='Ontology term that describes the phenotype.')
	negated = models.BooleanField(default=False,
		help_text='This element is a flag to indicate whether the phenotype was observed or not.')
	severity = JSONField(blank=True, null=True,
		help_text='Description of the severity of the feature'
		'represented by a term from HP:0012824.')
	modifier = ArrayField(JSONField(null=True, blank=True), blank=True, null=True,
		help_text='This element is  intended to provide more expressive or precise '
		'descriptions of a phenotypic feature, including attributes such as positionality '
		'and external factors that tend to trigger or ameliorate the feature.')
	onset = JSONField(blank=True, null=True,
		help_text='This element can be used to describe the age at '
		'which a phenotypic feature was first noticed or diagnosed.')
	# evidence can stay here because evidence is given for an observation of PF
	# JSON schema to check evidence_code is present
	# FHIR: Condition.evidence
	evidence = JSONField(blank=True, null=True,
		help_text='This element intends to represent the evidence for '
		'an assertion such as an observation of a PhenotypicFeature.')
	biosample = models.ForeignKey("Biosample", on_delete=models.SET_NULL,
		blank=True, null=True, related_name='phenotypic_features')
	phenopacket = models.ForeignKey("Phenopacket", on_delete=models.SET_NULL,
		blank=True, null=True, related_name='phenotypic_features')

	def __str__(self):
		return str(self.id)


class Procedure(models.Model):
	"""
	Class to represent a clinical procedure performed on an individual
	(subject) in oder to extract a biosample

	FHIR: Procedure
	"""

	code = JSONField(help_text='Clinical procedure performed on a subject.')
	body_site = JSONField(blank=True, null=True,
		help_text='Specific body site if unable to represent this is the code.')

	def __str__(self):
		return str(self.id)

	def indexing(self):
		# mapping model fields to index fields
		obj = ProcedureIndex(
			meta={'id': self.id},
			resourceType='Procedure',
			identifier=self.id,
			code=InnerDoc(
				properties={
				'coding': InnerDoc(
					properties={
					'system': '',
					'code': self.code.get('id', None),
					'display':self.code.get('label', None)
					}
					)
				}
				),
			bodySite=InnerDoc(
				properties={
				'coding': InnerDoc(
					properties={
					'system': '',
					'code': [self.body_site.get('id', None) if self.body_site else ''][0],
					'display': [self.body_site.get('label', None) if self.body_site else ''][0]
					}
					)
				}
				)
			)
		obj.save(index='metadata')
		return obj.to_dict(include_meta=True)

	def delete_from_index(self):
		obj = ProcedureIndex.get(id=self.id, index='metadata')
		obj.delete()
		return

	def update_index(self):
		obj = self.indexing()
		return obj

# add to index on post_save signal
@receiver(post_save, sender=Procedure)
def index_procedure(sender, instance, **kwargs):
    instance.indexing()

# delete doc from index when instance is deleted in db
@receiver(post_delete, sender=Procedure)
def remove_procedure(sender, instance, **kwargs):
	instance.delete_from_index()

# update doc in index when instance is updated in db
@receiver(pre_save, sender=Procedure)
def update_procedure(sender, instance, *args, **kwargs):
	instance.update_index()


class HtsFile(models.Model):
	"""
	Class to link HTC files with data

	FHIR: DocumentReference
	"""

	HTS_FORMAT = (
		('UNKNOWN', 'UNKNOWN'),
		('SAM', 'SAM'),
		('BAM', 'BAM'),
		('CRAM', 'CRAM'),
		('VCF', 'VCF'),
		('BCF', 'BCF'),
		('GVCF', 'GVCF')
	)
	uri = models.URLField(primary_key=True, max_length=200,
		help_text='A valid URI for the file.')
	description = models.CharField(max_length=200, blank=True,
		help_text='An arbitrary description of the file contents.')
	hts_format = models.CharField(max_length=200, choices=HTS_FORMAT,
		help_text="A format of the file.")
	genome_assembly = models.CharField(max_length=200,
		help_text='The genome assembly the contents of this file was called against.')
	# e.g.
	# "individualToSampleIdentifiers": {
	#   "patient23456": "NA12345"
	# TODO how to perform this validation, ensure the patient id is the correct one?
	individual_to_sample_identifiers = JSONField(blank=True, null=True,
		help_text='The mapping between the Individual.id or Biosample.id '
		'to the sample identifier in the HTS file')

	def __str__(self):
		return str(self.uri)


class Gene(models.Model):
	"""
	Class to represent an identifier for a gene

	FHIR: ?
	Draft extention for Gene is in development
	where Gene defined via class CodeableConcept
	"""

	# Gene id is unique
	gene_id = models.CharField(primary_key=True, max_length=200,
		help_text='Official identifier of the gene.')
	# CURIE style? Yes!
	alternate_id = ArrayField(models.CharField(max_length=200, blank=True),
		blank=True, null=True,
		help_text='Alternative identifier(s) of the gene.')
	symbol = models.CharField(max_length=200,
		help_text='Official gene symbol.')

	def __str__(self):
		return str(self.gene_id)


class Variant(models.Model):
	"""
	Class to describe Individual variants or diagnosed causative variants

	FHIR: Observation ?
	Draft extention for Variant is in development
	"""

	ALLELE = (
		('hgvsAllele', 'hgvsAllele'),
		('vcfAllele', 'vcfAllele'),
		('spdiAllele', 'spdiAllele'),
		('iscnAllele', 'iscnAllele')
	)
	allele_type = models.CharField(max_length=200, choices=ALLELE,
		help_text='One of four allele types.')
	allele = JSONField()
	zygosity = JSONField(blank=True, null=True,
		help_text='Genotype Ontology (GENO) term representing the zygosity of the variant.')

	def __str__(self):
		return str(self.id)


class Disease(models.Model):
	"""
	Class to represent a diagnosis and inference or hypothesis about the cause
	underlying the observed phenotypic abnormalities

	FHIR: Condition
	"""

	term = JSONField(help_text='An ontology term that represents the disease.')
	# "ageOfOnset": {
	# "age": "P38Y7M"
	# }
	# OR
	# "ageOfOnset": {
	# "id": "HP:0003581",
	# "label": "Adult onset"
	# }
	age_of_onset = JSONField(blank=True, null=True,
		help_text='An element representing the age of onset of the disease.')
	tumor_stage = ArrayField(JSONField(null=True, blank=True),
		blank=True, null=True,
		help_text='List of terms representing the tumor stage (TNM findings).')

	def __str__(self):
		return str(self.id)


class Biosample(models.Model):
	"""
	Class to describe a unit of biological material

	FHIR: Specimen
	"""

	biosample_id = models.CharField(primary_key=True, max_length=200,
		help_text='An arbitrary identifier.')
	# if Individual instance is deleted Biosample instance is deleted too
	individual = models.ForeignKey(Individual, on_delete=models.CASCADE,
		blank=True, null=True, related_name='biosamples',
		help_text='The id of the Individual this biosample was derived from.')
	description = models.CharField(max_length=200, blank=True,
		help_text='The biosample’s description.')
	sampled_tissue = JSONField(help_text='An Ontology term describing '
		'the tissue from which the sample was taken.')
	# phenotypic_features = models.ManyToManyField(PhenotypicFeature, blank=True,
	# 	help_text='List of phenotypic abnormalities of the sample.')
	taxonomy = JSONField(blank=True, null=True,
		help_text='An Ontology term describing the species of the sampled individual.')
	# An ISO8601 string represent age
	individual_age_at_collection = models.CharField(max_length=200, blank=True,
		help_text='Age of the proband at the time the sample was taken.')
	histological_diagnosis = JSONField(blank=True, null=True,
		help_text='An Ontology term describing the disease diagnosis '
		'that was inferred from the histological examination.')
	tumor_progression = JSONField(blank=True, null=True,
		help_text='An Ontology term describing primary, metastatic, recurrent.')
	tumor_grade = JSONField(blank=True, null=True,
		help_text='An Ontology term describing the tumor grade. '
		'Potentially a child term of NCIT:C28076 or equivalent.')
	diagnostic_markers =  ArrayField(JSONField(null=True, blank=True),
		blank=True, null=True,
		help_text='List of Ontology terms describing clinically relevant biomarkers.')
	# CHECK! if Procedure instance is deleted Biosample instance is deleted too
	procedure = models.ForeignKey(Procedure, on_delete=models.CASCADE,
		help_text='The procedure used to extract the biosample.')
	hts_files = models.ManyToManyField(HtsFile, blank=True,
		related_name='biosample_hts_files',
		help_text='List of high-throughput sequencing files derived from the biosample.')
	variants = models.ManyToManyField(Variant, blank=True,
		help_text='List of variants determined to be present in the biosample.')
	is_control_sample = models.BooleanField(default=False,
		help_text='Whether the sample is being used as a normal control.')

	def __str__(self):
		return str(self.biosample_id)

	@property
	def get_sample_tissue_data(self):
		return {'reference': {
			'reference': self.sampled_tissue.get('id'),
			'display': self.sampled_tissue.get('label')
			}
		}

	def indexing(self):
		# mapping model fields to index fields
		if self.individual:
			subject = self.individual.individual_id
		else:
			subject = None
		obj = BiosampleIndex(
			meta={'id': self.biosample_id},
			resourceType='Specimen',
			identifier=self.biosample_id,
			subject=subject,
			text=self.description,
			parent=InnerDoc(
				properties={
				'reference': InnerDoc(
					properties={
					'reference': self.sampled_tissue.get('id'),
					'display': self.sampled_tissue.get('label')
					}
					)
				}
				)
			)
		obj.save(index='metadata')
		return obj.to_dict(include_meta=True)

	def delete_from_index(self):
		obj = BiosampleIndex.get(id=self.biosample_id, index='metadata')
		obj.delete()
		return

	def update_index(self):
		obj = self.indexing()
		return obj

# add to index on post_save signal
@receiver(post_save, sender=Biosample)
def index_biosample(sender, instance, **kwargs):
    instance.indexing()

# delete doc from index when instance is deleted in db
@receiver(post_delete, sender=Biosample)
def remove_biosample(sender, instance, **kwargs):
	instance.delete_from_index()

# update doc in index when instance is updated in db
@receiver(pre_save, sender=Biosample)
def update_biosample(sender, instance, *args, **kwargs):
	instance.update_index()


class Phenopacket(models.Model):
	"""
	Class to aggregate Individual's experiments data
	"""

	phenopacket_id = models.CharField(primary_key=True, max_length=200,
		help_text='An arbitrary identifier for the phenopacket.')
	# if Individual instance is deleted Phenopacket instance is deleted too
	# CHECK !!! Force as required?
	subject = models.ForeignKey(Individual, on_delete=models.CASCADE,
		related_name='phenopackets', help_text='The proband.')
	# PhenotypicFeatures are present in Biosample, so can be accessed via Biosample instance
	# phenotypic_features = models.ManyToManyField(PhenotypicFeature, blank=True,
	# 	help_text='Phenotypic features observed in the proband.')
	biosamples = models.ManyToManyField(Biosample, blank=True,
		help_text='The biosamples that have been derived from an individual who is '
		'the subject of the Phenopacket. Rr a collection of biosamples in isolation.')
	genes = models.ManyToManyField(Gene, blank=True,
		help_text='Gene deemed to be relevant to the case.')
	variants = models.ManyToManyField(Variant, blank=True,
		help_text='Variants identified in the proband.')
	diseases = models.ManyToManyField(Disease, blank=True,
		help_text='Disease(s) diagnosed in the proband.')
	hts_files = models.ManyToManyField(HtsFile, blank=True,
		help_text='VCF or other high-throughput sequencing files.')
	# TODO OneToOneField
	meta_data = models.ForeignKey(MetaData, on_delete=models.CASCADE,
		help_text='Information about ontologies and references used in the phenopacket.')

	dataset = models.ForeignKey("chord.Dataset", on_delete=models.CASCADE, blank=True, null=True)

	def __str__(self):
		return str(self.phenopacket_id)


#############################################################
#                                                           #
#                    Interpretation                         #
#                                                           #
#############################################################


class GenomicInterpretation(models.Model):
	"""
	Class to represent a statemenet about the contribution
	of a genomic element towards the observed phenotype

	FHIR: Observation
	"""

	GENOMIC_INTERPRETATION_STATUS = (
		('UNKNOWN', 'UNKNOWN'),
		('REJECTED', 'REJECTED'),
		('CANDIDATE', 'CANDIDATE'),
		('CAUSATIVE', 'CAUSATIVE')
		)
	status = models.CharField(max_length=200, choices=GENOMIC_INTERPRETATION_STATUS,
		help_text='How the call of this GenomicInterpretation was interpreted.')
	gene = models.ForeignKey(Gene, on_delete=models.CASCADE, to_field='gene_id',
		blank=True, null=True,
		help_text='The gene contributing to the diagnosis.')
	variant = models.ForeignKey(Variant, on_delete=models.CASCADE,
		blank=True, null=True,
		help_text='The variant contributing to the diagnosis.')

	def clean(self):
		if not (self.gene or self.variant):
			raise ValidationError('Either Gene or Variant must be specified')

	def __str__(self):
		return str(self.id)


class Diagnosis(models.Model):
	"""
	Class to refer to disease that is present in the individual analyzed

	FHIR: Condition
	"""

	disease = models.ForeignKey(Disease, on_delete=models.CASCADE,
		help_text='The diagnosed condition.')
	# required?
	genomic_interpretations = models.ManyToManyField(GenomicInterpretation, blank=True,
		help_text='The genomic elements assessed as being responsible for the disease.')

	def __str__(self):
		return str(self.id)


class Interpretation(models.Model):
	"""
	Class to represent the interpretation of a genomic analysis

	FHIR: DiagnosticReport
	"""

	RESOLUTION_STATUS = (
		('UNKNOWN', 'UNKNOWN'),
		('SOLVED', 'SOLVED'),
		('UNSOLVED', 'UNSOLVED'),
		('IN_PROGRESS', 'IN_PROGRESS')
	)

	interpretation_id = models.CharField(max_length=200,
		help_text='An arbitrary identifier for the interpretation.')
	resolution_status = models.CharField(choices=RESOLUTION_STATUS, max_length=200,
		blank=True, help_text='The current status of work on the case.')
	# In Phenopackets schema this field is 'phenopacket_or_family'
	phenopacket = models.ForeignKey(Phenopacket, on_delete=models.CASCADE,
		related_name='interpretations',
		help_text='The subject of this interpretation.')
	# fetch disease via from phenopacket
	# diagnosis on one disease ? there can be many disease associated with phenopacket
	diagnosis = models.ManyToManyField(Diagnosis,
		help_text='One or more diagnoses, if made.')
	meta_data = models.ForeignKey(MetaData, on_delete=models.CASCADE,
		help_text='Metadata about this interpretation.')

	def __str__(self):
		return str(self.id)
